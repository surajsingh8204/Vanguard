import logging
import math

from typing import Any

from backend.src.services.artifact_service import artifact_service

logger = logging.getLogger(__name__)


class EvaluationService:

    def _json_safe(self, value: Any) -> Any:

        if isinstance(value, dict):
            return {
                key: self._json_safe(item)
                for key, item in value.items()
            }

        if isinstance(value, list):
            return [
                self._json_safe(item)
                for item in value
            ]

        if isinstance(value, tuple):
            return [
                self._json_safe(item)
                for item in value
            ]

        if isinstance(value, float) and not math.isfinite(value):
            return None

        return value

    def summary(self):

        coherence = artifact_service.load_json(
            "evaluation/coherence.json",
            default={},
        )
        purity = artifact_service.load_json(
            "evaluation/purity.json",
            default={},
        )
        forecast_evaluation = artifact_service.load_json(
            "evaluation/forecast_evaluation.json",
            default={},
        )
        correlation = artifact_service.load_json(
            "evaluation/correlation.json",
            default={},
        )
        label_audit = artifact_service.load_json(
            "evaluation/label_audit.json",
            default=[],
        )
        pipeline_status = artifact_service.load_json(
            "metadata/pipeline_status.json",
            default={},
        )

        return self._json_safe({
            "metadata": {
                "coherence_count": len(coherence),
                "purity_count": len(purity),
                "label_audit_count": len(label_audit),
                "status": pipeline_status.get("status", "unknown"),
            },
            "coherence": artifact_service.load_json(
                "evaluation/coherence.json",
                default={},
            ),
            "purity": artifact_service.load_json(
                "evaluation/purity.json",
                default={},
            ),
            "forecast_evaluation": artifact_service.load_json(
                "evaluation/forecast_evaluation.json",
                default={},
            ),
            "correlation": artifact_service.load_json(
                "evaluation/correlation.json",
                default={},
            ),
            "label_audit": artifact_service.load_json(
                "evaluation/label_audit.json",
                default={},
            ),
            "pipeline_status": artifact_service.load_json(
                "metadata/pipeline_status.json",
                default={},
            ),
        })


evaluation_service = EvaluationService()