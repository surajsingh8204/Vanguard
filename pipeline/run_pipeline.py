from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
if str(REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_ROOT))

from pipeline.logger import configure_logging
from pipeline.orchestrator import (
    STAGES,
    PipelineConfig,
    PipelineConfigurationError,
    PipelineOrchestrator,
    PipelineStageError,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run the complete Vanguard intelligence pipeline.",
    )
    parser.add_argument(
        "--config",
        default="pipeline/config.yaml",
        help="Path to pipeline YAML configuration (default: pipeline/config.yaml)",
    )
    parser.add_argument(
        "--no-resume",
        action="store_true",
        help="Discard incomplete orchestration state and start a new run.",
    )
    parser.add_argument(
        "--from-stage",
        choices=STAGES,
        help="Rerun this stage and every following stage.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate configuration and print the execution plan without running.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    original_directory = Path.cwd()
    config_path = Path(args.config)
    if not config_path.is_absolute():
        candidate = (original_directory / config_path).resolve()
        config_path = (
            candidate
            if candidate.exists()
            else (REPOSITORY_ROOT / config_path).resolve()
        )

    os.chdir(REPOSITORY_ROOT)

    try:
        config = PipelineConfig.load(config_path)
        logger = configure_logging(config.section("logging"))
        orchestrator = PipelineOrchestrator(
            config,
            logger,
            resume=False if args.no_resume else None,
            dry_run=args.dry_run,
            from_stage=args.from_stage,
        )
        orchestrator.run()
        return 0
    except PipelineConfigurationError as exc:
        print(f"Pipeline configuration error: {exc}", file=sys.stderr)
        return 2
    except PipelineStageError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print(
            "Pipeline interrupted. Rerun the same command to resume from the last checkpoint.",
            file=sys.stderr,
        )
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
