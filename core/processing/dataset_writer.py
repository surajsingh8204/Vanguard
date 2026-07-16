from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Any

from core.config.settings import ENRICHED_ARTICLES_PATH


logger = logging.getLogger(__name__)


@dataclass(slots=True)
class DatasetWriterReport:
    articles_saved: int = 0
    output_size_bytes: int = 0
    output_path: str = ""


class DatasetWriter:
    """Save processed datasets to disk using an atomic replace."""

    def __init__(self, output_path: str | Path = ENRICHED_ARTICLES_PATH) -> None:
        self.output_path = Path(output_path)
        self.report = DatasetWriterReport(output_path=self.output_path.as_posix())

    def write(self, articles: list[dict[str, Any]]) -> Path:
        self.output_path.parent.mkdir(parents=True, exist_ok=True)

        with NamedTemporaryFile(
            "w",
            encoding="utf-8",
            dir=self.output_path.parent,
            suffix=".tmp",
            delete=False,
        ) as handle:
            json.dump(articles, handle, indent=2, ensure_ascii=False)
            handle.write("\n")
            temp_path = Path(handle.name)

        temp_path.replace(self.output_path)
        self.report = DatasetWriterReport(
            articles_saved=len(articles),
            output_size_bytes=self.output_path.stat().st_size,
            output_path=self.output_path.as_posix(),
        )
        logger.info("Saved %s articles to %s", len(articles), self.output_path)
        self.print_report()
        return self.output_path

    def print_report(self) -> None:
        print("========================================")
        print()
        print("DATASET REPORT")
        print()
        print("========================================")
        print()
        print(f"Articles Saved: {self.report.articles_saved}")
        print()
        print(f"Output Size: {self.report.output_size_bytes} bytes")
        print()
        print(f"Output Path: {self.report.output_path}")
        print()
        print("========================================")
