from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Any


LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def configure_logging(config: dict[str, Any]) -> logging.Logger:
    """Configure orchestration and reused core-engine logging for this process."""

    level_name = str(config.get("level", "INFO")).upper()
    level = getattr(logging, level_name, logging.INFO)
    log_directory = Path(str(config["directory"]))
    log_directory.mkdir(parents=True, exist_ok=True)
    log_path = log_directory / str(config["filename"])

    logger = logging.getLogger("vanguard.pipeline")
    logger.setLevel(level)
    logger.propagate = False
    logger.handlers.clear()

    formatter = logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT)
    file_handler = RotatingFileHandler(
        log_path,
        maxBytes=int(config["rotate_bytes"]),
        backupCount=int(config["backup_count"]),
        encoding="utf-8",
    )
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    handlers: list[logging.Handler] = [file_handler]
    if bool(config.get("console", True)):
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        handlers.append(console_handler)

    # The pipeline runs in its own process, so root handlers capture logs from
    # reused core engines without affecting the independently running backend.
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.handlers.clear()
    for handler in handlers:
        root_logger.addHandler(handler)

    logger.debug("Logging initialized at %s", log_path)
    return logger
