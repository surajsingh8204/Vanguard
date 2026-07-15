from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from config.settings import PROCESSED_FEEDS_FILE, RAW_ARTICLES_DIR


logger = logging.getLogger(__name__)


@dataclass(slots=True)
class RawStorageReport:
    articles_saved: int = 0
    output_file: str = "N/A"
    file_size: int = 0


def load_processed(tracker_file: str | Path = PROCESSED_FEEDS_FILE) -> set[str]:
    tracker_path = Path(tracker_file)

    if not tracker_path.exists():
        return set()

    try:
        with tracker_path.open("r", encoding="utf-8") as handle:
            return {line.strip() for line in handle if line.strip()}
    except OSError as exc:
        logger.exception("Unable to read tracker file %s: %s", tracker_path, exc)
        return set()


def mark_processed(filename: str, tracker_file: str | Path = PROCESSED_FEEDS_FILE) -> None:
    tracker_path = Path(tracker_file)
    tracker_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        with tracker_path.open("a", encoding="utf-8") as handle:
            handle.write(filename + "\n")
    except OSError as exc:
        logger.exception("Unable to update tracker file %s: %s", tracker_path, exc)


def save_articles(
    articles: list[dict[str, Any]],
    raw_articles_dir: str | Path = RAW_ARTICLES_DIR,
) -> str | None:
    if not articles:
        _print_report(RawStorageReport())
        return None

    now = datetime.utcnow()
    output_directory = (
        Path(raw_articles_dir)
        / f"{now.year:04d}"
        / f"{now.month:02d}"
        / f"{now.day:02d}"
    )
    output_directory.mkdir(parents=True, exist_ok=True)

    output_path = output_directory / f"gdelt_{now.strftime('%Y%m%d_%H%M%S')}.json"

    try:
        with output_path.open("w", encoding="utf-8") as handle:
            json.dump(articles, handle, indent=2, ensure_ascii=False)
            handle.write("\n")
    except OSError as exc:
        logger.exception("Unable to save raw articles to %s: %s", output_path, exc)
        return None

    report = RawStorageReport(
        articles_saved=len(articles),
        output_file=output_path.as_posix(),
        file_size=output_path.stat().st_size,
    )
    logger.info("Saved %s articles to %s", len(articles), output_path)
    _print_report(report)
    return output_path.as_posix()


def _print_report(report: RawStorageReport) -> None:
    print("=========================")
    print("RAW STORAGE REPORT")
    print("=========================")
    print(f"Articles Saved: {report.articles_saved}")
    print(f"Output File: {report.output_file}")
    print(f"File Size: {report.file_size}")
    print("=========================")
