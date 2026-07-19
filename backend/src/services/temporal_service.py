import logging

from backend.src.services.artifact_service import artifact_service

logger = logging.getLogger(__name__)


class TemporalService:

    def timeline(self):
        timeline = artifact_service.load_json(
            "analytics/timeline.json",
            default=None,
        )
        if not timeline:
            timeline = artifact_service.load_json(
                "narrative/timeline.json",
                default={},
            )

        forecasts = artifact_service.load_json(
            "analytics/forecasts.json",
            default=None,
        )
        if not forecasts:
            forecasts = artifact_service.load_json(
                "narrative/forecasts.json",
                default=[],
            )

        early_warnings = artifact_service.load_json(
            "analytics/early_warnings.json",
            default=None,
        )
        if not early_warnings:
            early_warnings = artifact_service.load_json(
                "narrative/early_warnings.json",
                default=[],
            )

        return {
            "timeline": timeline or {},
            "forecasts": forecasts or [],
            "early_warnings": early_warnings or [],
            "strategic_context": artifact_service.load_json(
                "analytics/strategic_context.json",
                default={},
            ) or artifact_service.load_json(
                "metadata/strategic_context.json",
                default={},
            ),
            "influence_scores": artifact_service.load_json(
                "analytics/influence_scores.json",
                default={},
            ),
            "evolution": artifact_service.load_json(
                "narrative/evolution.json",
                default={},
            ),
            "spikes": artifact_service.load_json(
                "narrative/spikes.json",
                default=[],
            ),
            "emerging": artifact_service.load_json(
                "narrative/emerging.json",
                default=[],
            ),
        }

    def detail(self):
        return self.timeline()


temporal_service = TemporalService()
