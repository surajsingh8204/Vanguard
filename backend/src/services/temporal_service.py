import logging

from backend.src.services.artifact_service import artifact_service

logger = logging.getLogger(__name__)


class TemporalService:

    def timeline(self):

        return {
            "timeline": artifact_service.load_json(
                "analytics/timeline.json",
                default=[],
            ),
            "forecasts": artifact_service.load_json(
                "analytics/forecasts.json",
                default=[],
            ),
            "early_warnings": artifact_service.load_json(
                "analytics/early_warnings.json",
                default=[],
            ),
            "strategic_context": artifact_service.load_json(
                "analytics/strategic_context.json",
                default={},
            ),
            "influence_scores": artifact_service.load_json(
                "analytics/influence_scores.json",
                default=[],
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