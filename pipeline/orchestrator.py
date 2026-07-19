from __future__ import annotations

import json
import logging
import os
import shutil
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter
from typing import Any, Callable, Iterator

import yaml


STAGES = (
    "ingestion",
    "preprocessing",
    "model_build",
    "analytics_artifacts",
    "validation",
)


class PipelineConfigurationError(ValueError):
    """Raised when pipeline/config.yaml is invalid."""


class PipelineStageError(RuntimeError):
    """Raised with actionable context when an isolated stage fails."""

    def __init__(self, stage: str, cause: Exception, state_file: Path) -> None:
        self.stage = stage
        self.cause = cause
        message = (
            f"Stage '{stage}' failed: {cause}. "
            f"Fix the reported cause and rerun python pipeline/run_pipeline.py; "
            f"progress will resume from {state_file}."
        )
        super().__init__(message)


@dataclass(frozen=True)
class PipelineConfig:
    values: dict[str, Any]
    source: Path

    @classmethod
    def load(cls, path: str | Path) -> "PipelineConfig":
        source = Path(path)
        if not source.exists():
            raise PipelineConfigurationError(f"Configuration file not found: {source}")

        with source.open("r", encoding="utf-8") as handle:
            values = yaml.safe_load(handle)

        if not isinstance(values, dict):
            raise PipelineConfigurationError("Pipeline configuration must be a YAML mapping")

        required_sections = {
            "pipeline",
            "ingestion",
            "preprocessing",
            "embeddings",
            "vector_database",
            "artifacts",
            "logging",
        }
        missing = sorted(required_sections - values.keys())
        if missing:
            raise PipelineConfigurationError(
                f"Missing configuration sections: {', '.join(missing)}"
            )

        cls._validate(values)
        return cls(values=values, source=source)

    @staticmethod
    def _validate(values: dict[str, Any]) -> None:
        positive_fields = (
            ("ingestion", "articles_limit"),
            ("ingestion", "hours_back"),
            ("preprocessing", "workers"),
            ("preprocessing", "stream_read_size_bytes"),
            ("embeddings", "embedding_batch_size"),
        )
        for section, field in positive_fields:
            value = values[section].get(field)
            if not isinstance(value, int) or value <= 0:
                raise PipelineConfigurationError(
                    f"{section}.{field} must be a positive integer"
                )

        for section in ("ingestion", "preprocessing"):
            batch_size = values[section].get("batch_size")
            if batch_size != "auto" and (
                not isinstance(batch_size, int) or batch_size <= 0
            ):
                raise PipelineConfigurationError(
                    f"{section}.batch_size must be 'auto' or a positive integer"
                )
            auto = values[section].get("auto_batch")
            if not isinstance(auto, dict):
                raise PipelineConfigurationError(
                    f"{section}.auto_batch must be a mapping"
                )
            for field in ("target_batches", "minimum", "maximum"):
                if not isinstance(auto.get(field), int) or auto[field] <= 0:
                    raise PipelineConfigurationError(
                        f"{section}.auto_batch.{field} must be a positive integer"
                    )
            if auto["minimum"] > auto["maximum"]:
                raise PipelineConfigurationError(
                    f"{section}.auto_batch.minimum cannot exceed maximum"
                )

        if values["vector_database"].get("vector_db") != "faiss":
            raise PipelineConfigurationError(
                "Only the repository's existing FAISS vector database is supported"
            )

    def section(self, name: str) -> dict[str, Any]:
        value = self.values[name]
        if not isinstance(value, dict):
            raise PipelineConfigurationError(f"{name} must be a mapping")
        return value


class PipelineState:
    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self.data = self._load()

    def _load(self) -> dict[str, Any]:
        if not self.path.exists():
            return self._empty()
        try:
            with self.path.open("r", encoding="utf-8") as handle:
                value = json.load(handle)
        except (OSError, json.JSONDecodeError) as exc:
            raise PipelineConfigurationError(
                f"Unable to read pipeline state {self.path}: {exc}"
            ) from exc
        if not isinstance(value, dict):
            raise PipelineConfigurationError(
                f"Pipeline state must be a JSON object: {self.path}"
            )
        value.setdefault("stages", {})
        return value

    def _empty(self) -> dict[str, Any]:
        return {
            "version": 1,
            "status": "new",
            "created_at": _utc_now(),
            "updated_at": _utc_now(),
            "stages": {},
        }

    def begin_run(self, *, start_new_if_completed: bool = True) -> None:
        if self.data.get("status") == "completed" and start_new_if_completed:
            archive = self.path.with_name(
                f"{self.path.stem}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            )
            if self.path.exists():
                archive.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(self.path, archive)
            self.data = self._empty()
        self.data["status"] = "running"
        self.data["started_at"] = _utc_now()
        self.save()

    def reset_from(self, stage: str) -> None:
        if stage not in STAGES:
            raise PipelineConfigurationError(
                f"Unknown stage '{stage}'. Valid stages: {', '.join(STAGES)}"
            )
        index = STAGES.index(stage)
        for name in STAGES[index:]:
            self.data.get("stages", {}).pop(name, None)
        self.data["status"] = "running"
        self.save()

    def stage(self, name: str) -> dict[str, Any]:
        return self.data.setdefault("stages", {}).setdefault(name, {})

    def is_complete(self, name: str) -> bool:
        return self.stage(name).get("status") == "completed"

    def start_stage(self, name: str) -> None:
        stage = self.stage(name)
        stage.update(
            {
                "status": "running",
                "started_at": _utc_now(),
                "error": None,
            }
        )
        self.save()

    def update_stage(self, name: str, **details: Any) -> None:
        self.stage(name).update(details)
        self.save()

    def complete_stage(self, name: str, elapsed_seconds: float) -> None:
        self.stage(name).update(
            {
                "status": "completed",
                "completed_at": _utc_now(),
                "elapsed_seconds": round(elapsed_seconds, 3),
                "error": None,
            }
        )
        self.save()

    def fail_stage(self, name: str, exc: Exception) -> None:
        self.stage(name).update(
            {
                "status": "failed",
                "failed_at": _utc_now(),
                "error": f"{type(exc).__name__}: {exc}",
            }
        )
        self.data["status"] = "failed"
        self.save()

    def complete_run(self, elapsed_seconds: float) -> None:
        self.data.update(
            {
                "status": "completed",
                "completed_at": _utc_now(),
                "elapsed_seconds": round(elapsed_seconds, 3),
            }
        )
        self.save()

    def save(self) -> None:
        self.data["updated_at"] = _utc_now()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temporary = self.path.with_suffix(".tmp")
        with temporary.open("w", encoding="utf-8") as handle:
            json.dump(self.data, handle, indent=2, ensure_ascii=False)
            handle.write("\n")
        temporary.replace(self.path)


class PipelineOrchestrator:
    """Coordinate existing Vanguard engines and own only execution state."""

    def __init__(
        self,
        config: PipelineConfig,
        logger: logging.Logger,
        *,
        resume: bool | None = None,
        dry_run: bool = False,
        from_stage: str | None = None,
    ) -> None:
        self.config = config
        self.logger = logger
        self.dry_run = dry_run
        self.resume = (
            bool(config.section("pipeline").get("resume", True))
            if resume is None
            else resume
        )
        self.workspace = Path(str(config.section("pipeline")["workspace_dir"]))
        self.state = PipelineState(config.section("pipeline")["state_file"])
        self.from_stage = from_stage
        self._ai_pipeline = None

    def run(self) -> None:
        started_at = perf_counter()
        self.logger.info("=" * 72)
        self.logger.info("Pipeline Started: %s", self.config.section("pipeline")["name"])
        self.logger.info("Configuration: %s", self.config.source)
        self.logger.info("Resume enabled: %s", self.resume)

        if self.dry_run:
            self._log_execution_plan()
            self.logger.info("Dry run finished; no stages were executed")
            return

        if not self.resume:
            self.state.data = self.state._empty()
            self.state.save()
        self.state.begin_run(start_new_if_completed=self.from_stage is None)
        if self.from_stage:
            self.state.reset_from(self.from_stage)

        self._run_stage("ingestion", self._run_ingestion)
        self._run_stage("preprocessing", self._run_preprocessing)
        self._run_stage("model_build", self._run_model_build)
        self._run_stage("analytics_artifacts", self._run_analytics_artifacts)
        self._run_stage("validation", self._validate_artifacts)

        elapsed = perf_counter() - started_at
        self.state.complete_run(elapsed)
        self.logger.info("Pipeline Finished")
        self.logger.info("Total Time: %s", _format_duration(elapsed))
        self.logger.info("=" * 72)

    def _run_stage(self, name: str, action: Callable[[], None]) -> None:
        if self.resume and self.state.is_complete(name):
            self.logger.info("Skipping completed stage: %s", name)
            return

        self.logger.info("Running %s...", name.replace("_", " ").title())
        started_at = perf_counter()
        self.state.start_stage(name)
        try:
            action()
        except Exception as exc:
            self.state.fail_stage(name, exc)
            self.logger.exception("Stage failed: %s", name)
            raise PipelineStageError(name, exc, self.state.path) from exc
        elapsed = perf_counter() - started_at
        self.state.complete_stage(name, elapsed)
        self.logger.info(
            "Completed %s in %s",
            name.replace("_", " "),
            _format_duration(elapsed),
        )

    def _run_ingestion(self) -> None:
        from core.ingestion.gdelt_feed_ingest import GDELTFeedIngest

        settings = self.config.section("ingestion")
        target = int(settings["articles_limit"])
        batch_size = self._resolve_batch_size("ingestion", target)
        output_dir = self.workspace / "ingestion"
        output_dir.mkdir(parents=True, exist_ok=True)

        stage = self.state.stage("ingestion")
        completed_feeds = set(stage.get("completed_feeds", []))
        batch_files = [Path(path) for path in stage.get("batch_files", [])]
        article_count = int(stage.get("article_count", 0))
        seen_urls = self._restore_seen_urls(batch_files)

        engine = GDELTFeedIngest(hours_back=int(settings["hours_back"]))
        urls = engine.generate_feed_urls()

        for feed_index, url in enumerate(urls, start=1):
            if article_count >= target:
                break
            filename = url.rsplit("/", 1)[-1]
            if filename in completed_feeds:
                continue

            path = engine.download_feed(url)
            if not path:
                self.logger.warning("Feed download failed; continuing: %s", url)
                continue

            parsed = engine.parse_gkg(path)
            unique = []
            for article in parsed:
                article_url = article.get("url")
                if not article_url or article_url in seen_urls:
                    continue
                seen_urls.add(article_url)
                unique.append(article)
                if article_count + len(unique) >= target:
                    break

            for start in range(0, len(unique), batch_size):
                batch = unique[start:start + batch_size]
                batch_number = len(batch_files) + 1
                batch_path = output_dir / f"batch_{batch_number:06d}.json"
                _write_json_atomic(batch_path, batch)
                batch_files.append(batch_path)
                article_count += len(batch)
                self.logger.info(
                    "%s / %s articles ingested (feed %s / %s)",
                    article_count,
                    target,
                    feed_index,
                    len(urls),
                )

            engine.mark_processed(filename)
            completed_feeds.add(filename)
            self.state.update_stage(
                "ingestion",
                completed_feeds=sorted(completed_feeds),
                batch_files=[path.as_posix() for path in batch_files],
                article_count=article_count,
                target_articles=target,
                batch_size=batch_size,
            )

        if article_count == 0:
            raise RuntimeError(
                "Ingestion produced no articles. Check network access, GDELT availability, "
                "and ingestion.hours_back."
            )
        if article_count < target:
            self.logger.warning(
                "Ingestion completed below target: %s / %s articles. "
                "Increase ingestion.hours_back to scan more feeds.",
                article_count,
                target,
            )

    def _run_preprocessing(self) -> None:
        from core.processing.article_extractor import ArticleExtractor
        from core.processing.article_fetcher import ArticleFetcher
        from core.processing.batch_processor import BatchProcessor
        from core.processing.content_pipeline import ContentPipeline

        settings = self.config.section("preprocessing")
        ingestion = self.state.stage("ingestion")
        raw_batch_files = [Path(path) for path in ingestion.get("batch_files", [])]
        if not raw_batch_files:
            raise RuntimeError("No ingestion batch files are available for preprocessing")

        target = int(ingestion.get("article_count", 0))
        batch_size = self._resolve_batch_size("preprocessing", target)
        # A mid-stage resume must keep the batch size used by earlier batches,
        # otherwise next_batch_index would point at the wrong records.
        resumed_batch_size = int(self.state.stage("preprocessing").get("batch_size", 0))
        if resumed_batch_size > 0 and int(self.state.stage("preprocessing").get("next_batch_index", 0)) > 0:
            batch_size = resumed_batch_size
        workers = int(settings["workers"])
        output_path = Path(str(settings["output_path"]))
        accepted_jsonl = self.workspace / "preprocessing" / "accepted_articles.jsonl"
        accepted_jsonl.parent.mkdir(parents=True, exist_ok=True)

        stage = self.state.stage("preprocessing")
        next_batch_index = int(stage.get("next_batch_index", 0))
        accepted_count = int(stage.get("accepted_count", 0))
        rejected_count = int(stage.get("rejected_count", 0))
        if next_batch_index == 0:
            accepted_jsonl.unlink(missing_ok=True)

        engine = ContentPipeline(output_path=output_path)
        engine.batch_processor = BatchProcessor(batch_size=batch_size)
        engine.fetcher = ArticleFetcher(max_workers=workers)
        engine.extractor = ArticleExtractor(max_workers=workers)
        engine.firewall.reset_hashes()
        if next_batch_index > 0 and accepted_jsonl.exists():
            engine.firewall.seed_hashes(self._read_jsonl(accepted_jsonl))

        total_batches = sum(
            (self._json_list_length(path) + batch_size - 1) // batch_size
            for path in raw_batch_files
        )
        logical_batch_index = 0

        for raw_path in raw_batch_files:
            raw_articles = self._read_json_list(raw_path)
            raw_articles = engine.deduplicate_urls(raw_articles)
            raw_articles = engine.normalize_articles(raw_articles)

            for start in range(0, len(raw_articles), batch_size):
                if logical_batch_index < next_batch_index:
                    logical_batch_index += 1
                    continue

                batch = raw_articles[start:start + batch_size]
                self.logger.info(
                    "Processing batch %s / %s (%s articles). Fetching from "
                    "source sites is network-bound; individual fetch warnings "
                    "are normal.",
                    logical_batch_index + 1,
                    total_batches,
                    len(batch),
                )
                result = engine.process_batch(
                    batch,
                    logical_batch_index + 1,
                    total_batches,
                )
                self._append_jsonl(accepted_jsonl, result.accepted_articles)
                accepted_count += result.accepted_count
                rejected_count += result.rejected_count
                logical_batch_index += 1

                self.state.update_stage(
                    "preprocessing",
                    next_batch_index=logical_batch_index,
                    total_batches=total_batches,
                    accepted_count=accepted_count,
                    rejected_count=rejected_count,
                    batch_size=batch_size,
                    accepted_jsonl=accepted_jsonl.as_posix(),
                    output_path=output_path.as_posix(),
                )
                self.logger.info(
                    "%s / %s raw articles processed; %s accepted",
                    min(logical_batch_index * batch_size, target),
                    target,
                    accepted_count,
                )

        self._jsonl_to_json_array(accepted_jsonl, output_path)
        if accepted_count == 0:
            raise RuntimeError(
                "Preprocessing accepted zero articles. Review fetch/extraction logs and "
                "network access before resuming."
            )
        self.logger.info("Processed dataset written to %s", output_path)

    def _run_model_build(self) -> None:
        from core.config.settings import EMBEDDING_MODEL
        from core.embeddings.embedding_services import EmbeddingService
        from core.pipeline.ai_pipeline import AIPipeline

        embedding_settings = self.config.section("embeddings")
        vector_settings = self.config.section("vector_database")
        dataset_path = Path(
            str(self.config.section("preprocessing")["output_path"])
        )
        if not dataset_path.exists():
            raise FileNotFoundError(f"Processed dataset not found: {dataset_path}")

        model_name = str(
            embedding_settings.get(
                "model",
                f"sentence-transformers/{EMBEDDING_MODEL}",
            )
        )
        embedding_service = EmbeddingService(
            model_name=model_name,
            batch_size=int(embedding_settings["embedding_batch_size"]),
            device=embedding_settings.get("device"),
            checkpoint_dir=embedding_settings["checkpoint_dir"],
            save_every_batch=bool(embedding_settings["save_every_batch"]),
        )
        self._ai_pipeline = AIPipeline(embedding_service=embedding_service)

        self.logger.info(
            "Running Embeddings -> Narrative Clustering -> FAISS index build. "
            "The existing core finalizes FAISS after clustering because vector metadata "
            "contains cluster IDs."
        )
        self._ai_pipeline.build_vector_db(
            self._iter_json_array(dataset_path),
            force_rebuild=bool(vector_settings["rebuild_vectors"]),
            dataset_path=dataset_path.as_posix(),
        )
        self.state.update_stage(
            "model_build",
            embedding_batch_size=int(embedding_settings["embedding_batch_size"]),
            device=str(embedding_settings.get("device", "auto")),
            vector_db=str(vector_settings["vector_db"]),
            rebuild_vectors=bool(vector_settings["rebuild_vectors"]),
        )

    def _run_analytics_artifacts(self) -> None:
        from core.pipeline.ai_pipeline import AIPipeline

        if self._ai_pipeline is None:
            dataset_path = Path(
                str(self.config.section("preprocessing")["output_path"])
            )
            self._ai_pipeline = AIPipeline()
            self._ai_pipeline.build_vector_db(
                self._iter_json_array(dataset_path),
                force_rebuild=False,
                dataset_path=dataset_path.as_posix(),
            )

        rebuild = bool(
            self.config.section("artifacts").get("rebuild_artifacts", True)
        )
        self.logger.info(
            "Running Narrative Intelligence -> Evaluation -> Artifact Generation"
        )
        self._ai_pipeline.run_analytics(force_rebuild=rebuild)
        self.state.update_stage(
            "analytics_artifacts",
            rebuild_artifacts=rebuild,
        )

    def _validate_artifacts(self) -> None:
        required = [
            Path(str(path))
            for path in self.config.section("artifacts").get("required", [])
        ]
        missing = [path.as_posix() for path in required if not path.exists()]
        empty = [
            path.as_posix()
            for path in required
            if path.exists() and path.stat().st_size == 0
        ]
        if missing or empty:
            messages = []
            if missing:
                messages.append(f"missing: {', '.join(missing)}")
            if empty:
                messages.append(f"empty: {', '.join(empty)}")
            raise RuntimeError("Artifact validation failed (" + "; ".join(messages) + ")")
        self.state.update_stage(
            "validation",
            artifacts_checked=len(required),
        )
        self.logger.info("Validated %s required artifacts", len(required))

    def _resolve_batch_size(self, section_name: str, total: int) -> int:
        settings = self.config.section(section_name)
        configured = settings["batch_size"]
        if configured != "auto":
            return int(configured)

        auto = settings["auto_batch"]
        target_batches = int(auto["target_batches"])
        minimum = int(auto["minimum"])
        maximum = int(auto["maximum"])
        calculated = (max(total, 1) + target_batches - 1) // target_batches
        return max(minimum, min(maximum, calculated))

    def _restore_seen_urls(self, batch_files: list[Path]) -> set[str]:
        seen = set()
        for path in batch_files:
            if not path.exists():
                raise FileNotFoundError(
                    f"Ingestion checkpoint references missing batch: {path}"
                )
            for article in self._read_json_list(path):
                url = article.get("url")
                if url:
                    seen.add(str(url))
        return seen

    def _read_json_list(self, path: Path) -> list[dict[str, Any]]:
        with path.open("r", encoding="utf-8") as handle:
            value = json.load(handle)
        if not isinstance(value, list):
            raise ValueError(f"Expected JSON array in {path}")
        return [item for item in value if isinstance(item, dict)]

    def _json_list_length(self, path: Path) -> int:
        return len(self._read_json_list(path))

    def _read_jsonl(self, path: Path) -> list[dict[str, Any]]:
        if not path.exists():
            return []
        items: list[dict[str, Any]] = []
        with path.open("r", encoding="utf-8") as handle:
            for line in handle:
                value = line.strip()
                if not value:
                    continue
                item = json.loads(value)
                if isinstance(item, dict):
                    items.append(item)
        return items

    def _append_jsonl(
        self,
        path: Path,
        items: list[dict[str, Any]],
    ) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as handle:
            for item in items:
                handle.write(json.dumps(item, ensure_ascii=False))
                handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())

    def _jsonl_to_json_array(self, source: Path, destination: Path) -> None:
        destination.parent.mkdir(parents=True, exist_ok=True)
        temporary = destination.with_suffix(".tmp")
        with source.open("r", encoding="utf-8") as input_handle:
            with temporary.open("w", encoding="utf-8") as output_handle:
                output_handle.write("[\n")
                first = True
                for line in input_handle:
                    value = line.strip()
                    if not value:
                        continue
                    if not first:
                        output_handle.write(",\n")
                    output_handle.write(value)
                    first = False
                output_handle.write("\n]\n")
        temporary.replace(destination)

    def _iter_json_array(self, path: Path) -> Iterator[dict[str, Any]]:
        read_size = int(
            self.config.section("preprocessing")["stream_read_size_bytes"]
        )
        decoder = json.JSONDecoder()
        with path.open("r", encoding="utf-8") as handle:
            buffer = ""
            started = False
            finished = False

            while not finished:
                chunk = handle.read(read_size)
                if chunk:
                    buffer += chunk
                elif not buffer.strip():
                    break

                position = 0
                while True:
                    while position < len(buffer) and (
                        buffer[position].isspace() or buffer[position] == ","
                    ):
                        position += 1

                    if not started:
                        if position >= len(buffer):
                            break
                        if buffer[position] != "[":
                            raise ValueError(f"Expected JSON array in {path}")
                        started = True
                        position += 1
                        continue

                    while position < len(buffer) and (
                        buffer[position].isspace() or buffer[position] == ","
                    ):
                        position += 1
                    if position < len(buffer) and buffer[position] == "]":
                        finished = True
                        position += 1
                        break
                    if position >= len(buffer):
                        break

                    try:
                        value, end = decoder.raw_decode(buffer, position)
                    except json.JSONDecodeError:
                        if chunk:
                            break
                        raise
                    if isinstance(value, dict):
                        yield value
                    position = end

                buffer = buffer[position:]
                if not chunk and buffer.strip():
                    raise ValueError(f"Incomplete JSON array in {path}")

    def _log_execution_plan(self) -> None:
        ingestion = self.config.section("ingestion")
        preprocessing = self.config.section("preprocessing")
        embeddings = self.config.section("embeddings")
        self.logger.info("Execution plan:")
        self.logger.info(
            "  1. Ingestion: target=%s hours_back=%s batch_size=%s",
            ingestion["articles_limit"],
            ingestion["hours_back"],
            ingestion["batch_size"],
        )
        self.logger.info(
            "  2. Preprocessing: batch_size=%s workers=%s",
            preprocessing["batch_size"],
            preprocessing["workers"],
        )
        self.logger.info(
            "  3-5. Core model build: embedding_batch=%s device=%s vector_db=%s",
            embeddings["embedding_batch_size"],
            embeddings["device"],
            self.config.section("vector_database")["vector_db"],
        )
        self.logger.info(
            "  6-8. Narrative intelligence, evaluation, and all artifacts"
        )


def _write_json_atomic(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(".tmp")
    with temporary.open("w", encoding="utf-8") as handle:
        json.dump(value, handle, indent=2, ensure_ascii=False)
        handle.write("\n")
    temporary.replace(path)


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _format_duration(seconds: float) -> str:
    total = max(0, int(seconds))
    hours, remainder = divmod(total, 3600)
    minutes, remaining_seconds = divmod(remainder, 60)
    if hours:
        return f"{hours}h {minutes}m {remaining_seconds}s"
    if minutes:
        return f"{minutes}m {remaining_seconds}s"
    return f"{remaining_seconds}s"
