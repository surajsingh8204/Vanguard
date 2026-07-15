from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

from config.settings import BATCH_SIZE, CHECKPOINT_FILE


logger = logging.getLogger(__name__)


@dataclass(slots=True)
class BatchCheckpoint:
    dataset: str
    batch: int
    processed_articles: int
    completed: bool = False


class BatchProcessor:
    def __init__(
        self,
        batch_size: int = BATCH_SIZE,
        checkpoint_file: str | Path = CHECKPOINT_FILE,
    ) -> None:
        if batch_size <= 0:
            raise ValueError("batch_size must be greater than zero")

        self.batch_size = batch_size
        self.checkpoint_file = Path(checkpoint_file)
        self.accepted_state_file = self.checkpoint_file.with_name(
            f"{self.checkpoint_file.stem}_accepted.json"
        )

    def create_batches(self, items: list[dict[str, Any]]) -> Iterable[list[dict[str, Any]]]:
        for index in range(0, len(items), self.batch_size):
            yield items[index:index + self.batch_size]

    def save_checkpoint(
        self,
        batch_number: int,
        dataset: str,
        processed_articles: int,
        completed: bool = False,
    ) -> None:
        self.checkpoint_file.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "dataset": dataset,
            "batch": batch_number,
            "processed_articles": processed_articles,
            "completed": completed,
        }

        try:
            with self.checkpoint_file.open("w", encoding="utf-8") as handle:
                json.dump(payload, handle, indent=2)
                handle.write("\n")
        except OSError as exc:
            logger.exception("Unable to save ETL checkpoint to %s: %s", self.checkpoint_file, exc)

    def load_checkpoint(self) -> BatchCheckpoint | None:
        if not self.checkpoint_file.exists():
            return None

        try:
            with self.checkpoint_file.open("r", encoding="utf-8") as handle:
                payload = json.load(handle)
        except (OSError, json.JSONDecodeError) as exc:
            logger.warning("Unable to read ETL checkpoint from %s: %s", self.checkpoint_file, exc)
            return None

        if not isinstance(payload, dict):
            return None

        dataset = payload.get("dataset")
        batch = payload.get("batch")
        processed_articles = payload.get("processed_articles")
        completed = payload.get("completed", False)

        if not isinstance(dataset, str):
            return None
        if not isinstance(batch, int):
            return None
        if not isinstance(processed_articles, int):
            return None
        if not isinstance(completed, bool):
            return None

        return BatchCheckpoint(
            dataset=dataset,
            batch=batch,
            processed_articles=processed_articles,
            completed=completed,
        )

    def clear_checkpoint(self) -> None:
        try:
            self.checkpoint_file.unlink(missing_ok=True)
        except OSError as exc:
            logger.warning("Unable to clear ETL checkpoint %s: %s", self.checkpoint_file, exc)

        try:
            self.accepted_state_file.unlink(missing_ok=True)
        except OSError as exc:
            logger.warning("Unable to clear ETL accepted state %s: %s", self.accepted_state_file, exc)

    def save_accepted_articles(
        self,
        dataset: str,
        articles: list[dict[str, Any]],
    ) -> None:
        self.accepted_state_file.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "dataset": dataset,
            "articles": articles,
        }

        try:
            with self.accepted_state_file.open("w", encoding="utf-8") as handle:
                json.dump(payload, handle, indent=2, ensure_ascii=False)
                handle.write("\n")
        except OSError as exc:
            logger.exception("Unable to save ETL accepted state to %s: %s", self.accepted_state_file, exc)

    def load_accepted_articles(self, dataset: str) -> list[dict[str, Any]]:
        if not self.accepted_state_file.exists():
            return []

        try:
            with self.accepted_state_file.open("r", encoding="utf-8") as handle:
                payload = json.load(handle)
        except (OSError, json.JSONDecodeError) as exc:
            logger.warning("Unable to load ETL accepted state from %s: %s", self.accepted_state_file, exc)
            return []

        if not isinstance(payload, dict):
            return []
        if payload.get("dataset") != dataset:
            return []

        articles = payload.get("articles", [])
        if not isinstance(articles, list):
            return []

        return [article for article in articles if isinstance(article, dict)]
