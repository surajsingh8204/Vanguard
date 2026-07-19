from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
from time import perf_counter
from typing import Any

from core.config.settings import (
    BATCH_SIZE,
    ENRICHED_ARTICLES_PATH,
    MAX_ARTICLES_PER_RUN,
    RAW_ARTICLES_DIR,
)
from core.processing.article_extractor import ArticleExtractor
from core.processing.article_fetcher import ArticleFetcher
from core.processing.batch_processor import BatchCheckpoint, BatchProcessor
from core.processing.data_quality_firewall import DataQualityFirewall
from core.processing.dataset_writer import DatasetWriter
from core.processing.document_purifier import DocumentPurifier
from core.processing.metadata_validator import MetadataValidator
from core.processing.raw_loader import RawLoader
from core.utils.time_utils import TimeUtils


logger = logging.getLogger(__name__)


@dataclass(slots=True)
class PipelineBatchResult:
    accepted_articles: list[dict[str, Any]]
    accepted_count: int
    rejected_count: int
    elapsed_seconds: float


class ContentPipeline:
    """Orchestrate ETL stages using bounded batches and resumable checkpoints."""

    def __init__(self, raw_dir: str | Path = RAW_ARTICLES_DIR, output_path: str | Path = ENRICHED_ARTICLES_PATH) -> None:
        self.raw_dir = Path(raw_dir)
        self.output_path = Path(output_path)
        self.raw_loader = RawLoader(raw_directory=self.raw_dir)
        self.batch_processor = BatchProcessor(batch_size=BATCH_SIZE)
        self.fetcher = ArticleFetcher()
        self.extractor = ArticleExtractor()
        self.purifier = DocumentPurifier()
        self.firewall = DataQualityFirewall()
        self.metadata_validator = MetadataValidator()
        self.dataset_writer = DatasetWriter(output_path=self.output_path)
        self.stats = {
            "dataset": "N/A",
            "articles_loaded": 0,
            "batch_size": self.batch_processor.batch_size,
            "total_batches": 0,
            "articles_accepted": 0,
            "articles_rejected": 0,
            "execution_time": 0.0,
            "average_batch_time": 0.0,
        }

    def run(self) -> list[dict[str, Any]]:
        run_started_at = perf_counter()
        articles = self.load_articles()
        articles = self.deduplicate_urls(articles)
        dataset_name = self._resolve_dataset_name()
        batches = list(self.batch_processor.create_batches(articles))

        self.stats["dataset"] = dataset_name
        self.stats["articles_loaded"] = len(articles)
        self.stats["total_batches"] = len(batches)

        if not batches:
            self.write_dataset([])
            self.batch_processor.clear_checkpoint()
            self.stats["execution_time"] = perf_counter() - run_started_at
            self.print_report()
            return []

        checkpoint = self.batch_processor.load_checkpoint()
        start_batch_index, accepted_articles = self._restore_progress(checkpoint, dataset_name, batches)
        batch_timings: list[float] = []
        # Preserve content hashes across batches so duplicates are rejected
        # for the whole run, not only within each 250-record window.
        self.firewall.reset_hashes()
        if accepted_articles:
            self.firewall.seed_hashes(accepted_articles)

        for batch_index in range(start_batch_index, len(batches)):
            batch_number = batch_index + 1
            batch = batches[batch_index]
            batch_result = self.process_batch(batch, batch_number, len(batches))
            accepted_articles.extend(batch_result.accepted_articles)
            batch_timings.append(batch_result.elapsed_seconds)
            self.stats["articles_accepted"] += batch_result.accepted_count
            self.stats["articles_rejected"] += batch_result.rejected_count

            processed_articles = min(batch_number * self.batch_processor.batch_size, len(articles))
            self.batch_processor.save_accepted_articles(dataset_name, accepted_articles)
            self.batch_processor.save_checkpoint(
                batch_number=batch_number,
                dataset=dataset_name,
                processed_articles=processed_articles,
                completed=False,
            )

            self._print_progress(
                batch_number=batch_number,
                total_batches=len(batches),
                batch_size=len(batch),
                total_articles=len(articles),
                accepted=batch_result.accepted_count,
                rejected=batch_result.rejected_count,
                elapsed_total=perf_counter() - run_started_at,
                batch_timings=batch_timings,
            )

        self.write_dataset(accepted_articles)
        self.batch_processor.clear_checkpoint()
        self.stats["execution_time"] = perf_counter() - run_started_at
        self.stats["average_batch_time"] = (
            sum(batch_timings) / len(batch_timings) if batch_timings else 0.0
        )
        self.print_report()
        return accepted_articles

    def load_articles(self) -> list[dict[str, Any]]:
        print("Loading raw articles...")
        articles = self.raw_loader.load_incremental(max_articles=MAX_ARTICLES_PER_RUN)
        normalized_articles = self.normalize_articles(articles)

        print(f"Loaded {len(normalized_articles)} raw articles")
        return normalized_articles

    def normalize_articles(
        self,
        articles: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """Normalize raw article metadata before bounded batch processing."""
        normalized_articles: list[dict[str, Any]] = []
        for article in articles:
            normalized_article = dict(article)
            raw_time = normalized_article.get("formatted_date") or normalized_article.get("date")
            if raw_time and not normalized_article.get("formatted_date"):
                normalized_article["formatted_date"] = TimeUtils.format_gdelt_time(raw_time)
            normalized_articles.append(normalized_article)

        return normalized_articles

    def deduplicate_urls(self, articles: list[dict[str, Any]]) -> list[dict[str, Any]]:
        seen_urls: set[str] = set()
        unique_articles: list[dict[str, Any]] = []

        for article in articles:
            url = article.get("url")
            if not url:
                continue
            if url in seen_urls:
                continue
            seen_urls.add(url)
            unique_articles.append(article)

        return unique_articles

    def process_batch(
        self,
        batch: list[dict[str, Any]],
        batch_number: int,
        total_batches: int,
    ) -> PipelineBatchResult:
        batch_started_at = perf_counter()
        print(f"Batch {batch_number} / {total_batches}")
        print("Processing articles")

        fetched_articles = self.fetcher.fetch_batch(batch)
        extracted_articles = self.extractor.extract_batch(fetched_articles)
        purified_articles = self.purifier.clean_batch(extracted_articles)
        screened_articles = self.firewall.validate_batch(purified_articles)
        validated_articles = self.metadata_validator.validate_batch(screened_articles)

        elapsed_seconds = perf_counter() - batch_started_at
        accepted_count = len(validated_articles)
        rejected_count = len(batch) - accepted_count

        return PipelineBatchResult(
            accepted_articles=validated_articles,
            accepted_count=accepted_count,
            rejected_count=rejected_count,
            elapsed_seconds=elapsed_seconds,
        )

    def write_dataset(self, articles: list[dict[str, Any]]) -> Path:
        print("Writing dataset...")
        output_path = self.dataset_writer.write(articles)
        print(f"Dataset written to: {output_path}")
        return output_path

    def print_report(self) -> None:
        print("==================================")
        print()
        print("CONTENT PIPELINE REPORT")
        print()
        print("==================================")
        print()
        print(f"Dataset: {self.stats['dataset']}")
        print()
        print(f"Articles Loaded: {self.stats['articles_loaded']}")
        print()
        print(f"Batch Size: {self.stats['batch_size']}")
        print()
        print(f"Total Batches: {self.stats['total_batches']}")
        print()
        print(f"Articles Accepted: {self.stats['articles_accepted']}")
        print()
        print(f"Articles Rejected: {self.stats['articles_rejected']}")
        print()
        print(f"Execution Time: {self._format_duration(self.stats['execution_time'])}")
        print()
        print(f"Average Batch Time: {self._format_duration(self.stats['average_batch_time'])}")
        print()
        print("==================================")

    def _resolve_dataset_name(self) -> str:
        report = self.raw_loader.report
        if report is None:
            return "N/A"
        if report.selected_dataset != "N/A":
            return report.selected_dataset
        if report.newest_dataset != "N/A":
            return Path(report.newest_dataset).name
        return "N/A"

    def _restore_progress(
        self,
        checkpoint: BatchCheckpoint | None,
        dataset_name: str,
        batches: list[list[dict[str, Any]]],
    ) -> tuple[int, list[dict[str, Any]]]:
        if checkpoint is None or checkpoint.completed:
            return 0, []

        if checkpoint.dataset != dataset_name:
            logger.info(
                "Ignoring checkpoint for dataset %s while processing %s",
                checkpoint.dataset,
                dataset_name,
            )
            self.batch_processor.clear_checkpoint()
            return 0, []

        completed_batches = max(0, min(checkpoint.batch, len(batches)))
        restored_articles = self.batch_processor.load_accepted_articles(dataset_name)
        if checkpoint.processed_articles > 0 and not restored_articles:
            logger.warning(
                "Checkpoint exists for %s but accepted article state is missing; restarting from batch 1",
                dataset_name,
            )
            self.batch_processor.clear_checkpoint()
            return 0, []

        restored_rejected = max(0, checkpoint.processed_articles - len(restored_articles))
        self.stats["articles_accepted"] = len(restored_articles)
        self.stats["articles_rejected"] = restored_rejected

        logger.info(
            "Resuming content pipeline from batch %s for dataset %s",
            completed_batches + 1,
            dataset_name,
        )
        print(f"Resuming from batch {completed_batches + 1} / {len(batches)}")
        return completed_batches, restored_articles

    def _print_progress(
        self,
        batch_number: int,
        total_batches: int,
        batch_size: int,
        total_articles: int,
        accepted: int,
        rejected: int,
        elapsed_total: float,
        batch_timings: list[float],
    ) -> None:
        article_start = ((batch_number - 1) * self.batch_processor.batch_size) + 1
        article_end = min(article_start + batch_size - 1, total_articles)
        remaining_batches = total_batches - batch_number
        average_batch_time = sum(batch_timings) / len(batch_timings) if batch_timings else 0.0
        estimated_remaining = average_batch_time * remaining_batches

        print(f"Accepted: {accepted}")
        print(f"Rejected: {rejected}")
        print(f"Articles {article_start}-{article_end}")
        print(f"Elapsed Time: {self._format_duration(elapsed_total)}")
        print(f"Estimated Remaining Time: {self._format_duration(estimated_remaining)}")

    def _format_duration(self, seconds: float) -> str:
        total_seconds = max(0, int(seconds))
        minutes, remaining_seconds = divmod(total_seconds, 60)
        hours, remaining_minutes = divmod(minutes, 60)
        if hours:
            return f"{hours}h {remaining_minutes}m {remaining_seconds}s"
        if minutes:
            return f"{minutes}m {remaining_seconds}s"
        return f"{remaining_seconds}s"


if __name__ == "__main__":
    ContentPipeline().run()
