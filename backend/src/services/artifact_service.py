"""
Artifact Service

Centralized access to all intelligence artifacts.

Responsibilities:
- Load JSON artifacts
- Save JSON artifacts
- Find latest evaluation reports
- Handle missing/corrupt files gracefully

All intelligence services should use this service.
"""

from __future__ import annotations

import json
import logging
import threading
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class ArtifactService:

    def __init__(self):

        # Project Root
        self.project_root = (
            Path(__file__)
            .resolve()
            .parents[3]
        )

        # Core artifacts
        self.artifacts_dir = (
            self.project_root
            / "core"
            / "artifacts"
        )

        # Historical reports
        self.logs_dir = (
            self.project_root
            / "evaluation_logs"
        )

        self._cache: dict[str, dict[str, Any]] = {}
        self._cache_lock = threading.Lock()

    # ---------------------------------------------------------
    # Generic Helpers
    # ---------------------------------------------------------

    def exists(
        self,
        relative_path: str,
    ) -> bool:

        return (
            self.artifacts_dir / relative_path
        ).exists()

    def load_json(
        self,
        relative_path: str,
        default: Any = None,
    ) -> Any:

        path = (
            self.artifacts_dir
            / relative_path
        )

        cache_key = str(path)
        try:
            mtime = path.stat().st_mtime
        except FileNotFoundError:
            logger.warning(
                "Artifact not found: %s",
                path,
            )
            return default

        with self._cache_lock:
            cached = self._cache.get(cache_key)
            if cached and cached.get("mtime") == mtime:
                return cached.get("data", default)

        try:

            with open(
                path,
                "r",
                encoding="utf-8",
            ) as f:

                return json.load(f)

        except Exception:

            logger.exception(
                "Unable to load artifact: %s",
                path,
            )

            return default

    def save_json(
        self,
        relative_path: str,
        data: Any,
    ):

        path = (
            self.artifacts_dir
            / relative_path
        )

        path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        try:

            with open(
                path,
                "w",
                encoding="utf-8",
            ) as f:

                json.dump(
                    data,
                    f,
                    indent=4,
                    ensure_ascii=False,
                )

            with self._cache_lock:
                self._cache[str(path)] = {
                    "mtime": path.stat().st_mtime,
                    "data": data,
                }

        except Exception:

            logger.exception(
                "Unable to save artifact: %s",
                path,
            )

    def load_report_json(
        self,
        filename: str,
        default: Any = None,
    ) -> Any:

        path = self.logs_dir / filename

        try:
            mtime = path.stat().st_mtime
        except FileNotFoundError:
            return default

        cache_key = str(path)

        with self._cache_lock:
            cached = self._cache.get(cache_key)
            if cached and cached.get("mtime") == mtime:
                return cached.get("data", default)

        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)

            with self._cache_lock:
                self._cache[cache_key] = {
                    "mtime": mtime,
                    "data": data,
                }

            return data
        except Exception:
            logger.exception("Unable to load report: %s", path)
            return default

    def list_reports(self):
        return sorted(
            self.logs_dir.glob("*.json"),
            key=lambda item: item.stat().st_mtime,
            reverse=True,
        )

    # ---------------------------------------------------------
    # Evaluation Reports
    # ---------------------------------------------------------

    def latest_report(
        self,
        prefix: str,
    ) -> Any:

        try:

            reports = sorted(
                self.logs_dir.glob(
                    f"{prefix}_*.json"
                ),
                reverse=True,
            )

            if not reports:
                return None

            with open(
                reports[0],
                "r",
                encoding="utf-8",
            ) as f:

                return json.load(f)

        except Exception:

            logger.exception(
                "Unable to load latest report."
            )

            return None


artifact_service = ArtifactService()