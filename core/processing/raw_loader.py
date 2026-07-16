from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable, Sequence

from core.config.settings import ARTIFACT_DIR, MAX_ARTICLES_PER_RUN, RAW_DIRECTORY, RAW_LOAD_MODE


logger = logging.getLogger(__name__)


@dataclass(slots=True)
class RawLoadReport:
    mode: str
    datasets_loaded: int = 0
    articles_loaded: int = 0
    selected_articles: int = 0
    newest_dataset: str = "N/A"
    oldest_dataset: str = "N/A"
    selected_dataset: str = "N/A"
    skipped_invalid_files: int = 0
    skipped_empty_files: int = 0
    loaded_datasets: set[Path] = field(default_factory=set)


class RawLoader:
    """Load raw article datasets from disk without performing downstream ETL."""

    def __init__(self, raw_directory: str | Path = RAW_DIRECTORY, artifact_dir: str | Path = ARTIFACT_DIR) -> None:
        self.raw_directory = Path(raw_directory)
        self.artifact_dir = Path(artifact_dir)
        self._report: RawLoadReport | None = None

    @property
    def report(self) -> RawLoadReport | None:
        return self._report

    def load_latest(self) -> list[dict[str, Any]]:
        datasets = self._select_latest_datasets(1)
        return self._load_selected(datasets, mode="latest")

    def load_last(self, n: int) -> list[dict[str, Any]]:
        if n <= 0:
            raise ValueError("load_last(n) requires n to be greater than zero")
        datasets = self._select_latest_datasets(n)
        return self._load_selected(datasets, mode=f"last_{n}")

    def load_since(self, since: datetime) -> list[dict[str, Any]]:
        if since.tzinfo is not None:
            since = since.replace(tzinfo=None)
        datasets = [item for item in self._discover_datasets() if item.timestamp > since]
        return self._load_selected(datasets, mode=f"since_{since.isoformat()}")

    def load_incremental(self, max_articles: int = MAX_ARTICLES_PER_RUN) -> list[dict[str, Any]]:
        if max_articles <= 0:
            raise ValueError("load_incremental(max_articles) requires a positive limit")

        datasets = self._select_latest_datasets(1)
        articles = self._load_selected(
            datasets,
            mode=f"incremental_max_{max_articles}",
            print_report=False,
        )
        sorted_articles = self._sort_articles_newest_first(articles)
        limited_articles = sorted_articles[:max_articles]

        if self._report is not None:
            self._report.selected_articles = len(limited_articles)
            if datasets:
                self._report.selected_dataset = datasets[-1].path.name
            self._print_report()

        return limited_articles

    def load_directory(self, path: str | Path) -> list[dict[str, Any]]:
        directory = Path(path)
        if not directory.exists():
            raise FileNotFoundError(f"Raw dataset directory does not exist: {directory}")
        if not directory.is_dir():
            raise NotADirectoryError(f"Raw dataset path is not a directory: {directory}")

        datasets = [
            item for item in self._discover_datasets(directory)
            if item.path.is_relative_to(directory)
        ]
        return self._load_selected(datasets, mode=f"directory:{directory}")

    def _load_selected(
        self,
        datasets: Sequence[DatasetFile],
        mode: str,
        print_report: bool = True,
    ) -> list[dict[str, Any]]:
        if not datasets:
            self._report = RawLoadReport(mode=mode)
            if print_report:
                self._print_report()
            return []

        unique_datasets = self._deduplicate_datasets(datasets)
        sorted_datasets = sorted(unique_datasets, key=lambda item: (item.timestamp, item.path.as_posix()))

        articles: list[dict[str, Any]] = []
        skipped_invalid = 0
        skipped_empty = 0

        for dataset in sorted_datasets:
            payload, skipped = self._load_dataset_file(dataset.path)
            if payload is None:
                if skipped == "empty":
                    skipped_empty += 1
                else:
                    skipped_invalid += 1
                continue
            articles.extend(payload)

        report = RawLoadReport(
            mode=mode,
            datasets_loaded=len(sorted_datasets) - skipped_invalid - skipped_empty,
            articles_loaded=len(articles),
            newest_dataset=sorted_datasets[-1].path.as_posix(),
            oldest_dataset=sorted_datasets[0].path.as_posix(),
            skipped_invalid_files=skipped_invalid,
            skipped_empty_files=skipped_empty,
            loaded_datasets={dataset.path for dataset in sorted_datasets},
        )
        self._report = report
        if print_report:
            self._print_report()
        logger.info(
            "Loaded %s datasets and %s articles in %s mode",
            report.datasets_loaded,
            report.articles_loaded,
            mode,
        )
        return articles

    def _load_dataset_file(self, path: Path) -> tuple[list[dict[str, Any]] | None, str | None]:
        try:
            if path.stat().st_size == 0:
                logger.warning("Skipping empty raw dataset: %s", path)
                return None, "empty"
        except OSError as exc:
            logger.exception("Unable to inspect raw dataset %s: %s", path, exc)
            return None, "invalid"

        try:
            with path.open("r", encoding="utf-8") as handle:
                payload = json.load(handle)
        except json.JSONDecodeError as exc:
            logger.warning("Skipping invalid JSON dataset %s: %s", path, exc)
            return None, "invalid"
        except OSError as exc:
            logger.exception("Unable to read raw dataset %s: %s", path, exc)
            return None, "invalid"

        articles = self._normalize_payload(payload, path)
        return articles, None

    def _normalize_payload(self, payload: Any, path: Path) -> list[dict[str, Any]]:
        if isinstance(payload, list):
            articles = [item for item in payload if isinstance(item, dict)]
            if len(articles) != len(payload):
                logger.warning("Ignored non-dictionary items in %s", path)
            return articles

        if isinstance(payload, dict):
            return [payload]

        logger.warning("Skipping unexpected payload type in %s", path)
        return []

    def _discover_datasets(self, root: Path | None = None) -> list[DatasetFile]:
        search_root = root or self.raw_directory
        if not search_root.exists():
            raise FileNotFoundError(f"Raw dataset directory does not exist: {search_root}")
        if not search_root.is_dir():
            raise NotADirectoryError(f"Raw dataset path is not a directory: {search_root}")

        datasets: list[DatasetFile] = []
        for path in search_root.rglob("*.json"):
            if path.is_file():
                timestamp = self._parse_dataset_timestamp(path)
                datasets.append(DatasetFile(path=path, timestamp=timestamp))

        return sorted(datasets, key=lambda item: (item.timestamp, item.path.as_posix()))

    def _select_latest_datasets(self, count: int) -> list[DatasetFile]:
        datasets = self._discover_datasets()
        if not datasets:
            raise FileNotFoundError(f"No raw JSON datasets found under {self.raw_directory}")
        return datasets[-count:]

    def _deduplicate_datasets(self, datasets: Iterable[DatasetFile]) -> list[DatasetFile]:
        unique: dict[Path, DatasetFile] = {}
        for dataset in datasets:
            unique[dataset.path.resolve()] = dataset
        return list(unique.values())

    def _parse_dataset_timestamp(self, path: Path) -> datetime:
        parts = path.relative_to(self.raw_directory).parts if self.raw_directory in path.parents or path == self.raw_directory else path.parts

        if len(parts) >= 4 and parts[-4].isdigit() and parts[-3].isdigit() and parts[-2].isdigit():
            year = int(parts[-4])
            month = int(parts[-3])
            day = int(parts[-2])
            stem = path.stem
            if stem.startswith("articles_"):
                stem = stem.removeprefix("articles_")
            time_parts = stem.split("_")
            if len(time_parts) >= 3 and all(item.isdigit() for item in time_parts[:3]):
                hour, minute, second = (int(item) for item in time_parts[:3])
                return datetime(year, month, day, hour, minute, second)
            if len(time_parts) >= 2 and all(item.isdigit() for item in time_parts[:2]):
                hour, minute = (int(item) for item in time_parts[:2])
                return datetime(year, month, day, hour, minute, 0)

        compact = path.stem
        if compact.startswith("articles_"):
            compact = compact.removeprefix("articles_")

        compact_digits = "".join(ch for ch in compact if ch.isdigit())
        if len(compact_digits) >= 14:
            return datetime.strptime(compact_digits[:14], "%Y%m%d%H%M%S")
        if len(compact_digits) >= 12:
            return datetime.strptime(compact_digits[:12], "%Y%m%d%H%M")
        if len(compact_digits) >= 8:
            return datetime.strptime(compact_digits[:8], "%Y%m%d")

        try:
            stat = path.stat()
        except OSError as exc:
            raise ValueError(f"Unable to derive dataset timestamp for {path}") from exc

        return datetime.fromtimestamp(stat.st_mtime)

    def _sort_articles_newest_first(self, articles: list[dict[str, Any]]) -> list[dict[str, Any]]:
        decorated: list[tuple[datetime, dict[str, Any]]] = []

        for article in articles:
            article_time = self._extract_article_timestamp(article)
            decorated.append((article_time, article))

        decorated.sort(key=lambda item: item[0], reverse=True)
        return [article for _, article in decorated]

    def _extract_article_timestamp(self, article: dict[str, Any]) -> datetime:
        for key in ("formatted_date", "date"):
            value = article.get(key)
            if not isinstance(value, str):
                continue
            parsed = self._parse_timestamp_value(value)
            if parsed is not None:
                return parsed

        return datetime.min

    def _parse_timestamp_value(self, value: str) -> datetime | None:
        normalized_value = value.strip()
        for formatter in (
            "%Y-%m-%dT%H:%M:%S.%f",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%d %H:%M:%S",
            "%Y%m%d%H%M%S",
            "%Y%m%d%H%M",
            "%Y%m%d",
        ):
            try:
                return datetime.strptime(normalized_value, formatter)
            except ValueError:
                continue
        return None

    def _print_report(self) -> None:
        report = self._report or RawLoadReport(mode=RAW_LOAD_MODE)
        print("========================================")
        print()
        print("RAW LOADER REPORT")
        print()
        print("========================================")
        print()
        print(f"Mode: {report.mode}")
        print()
        print(f"Datasets Loaded: {report.datasets_loaded}")
        print()
        print(f"Articles Loaded: {report.articles_loaded}")
        print()
        print(f"Selected Articles: {report.selected_articles}")
        print()
        print(f"Newest Dataset: {report.newest_dataset}")
        print()
        print(f"Oldest Dataset: {report.oldest_dataset}")
        print()
        print(f"Selected Dataset: {report.selected_dataset}")
        print()
        print(f"Skipped Invalid Files: {report.skipped_invalid_files}")
        print()
        print(f"Skipped Empty Files: {report.skipped_empty_files}")
        print()
        print("========================================")


@dataclass(slots=True, frozen=True)
class DatasetFile:
    path: Path
    timestamp: datetime
