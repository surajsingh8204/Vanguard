from backend.src.services.artifact_service import artifact_service


class DashboardService:

    def summary(self):
        pipeline_status = artifact_service.load_json(
            "metadata/pipeline_status.json",
            default={},
        )
        executive_brief = artifact_service.load_json(
            "metadata/executive_brief.json",
            default={},
        )
        strategic_context = artifact_service.load_json(
            "metadata/strategic_context.json",
            default={},
        )
        influence_scores = artifact_service.load_json(
            "analytics/influence_scores.json",
            default={},
        )
        forecasts = artifact_service.load_json(
            "analytics/forecasts.json",
            default=[],
        )
        early_warnings = artifact_service.load_json(
            "analytics/early_warnings.json",
            default=[],
        )
        timeline = artifact_service.load_json(
            "analytics/timeline.json",
            default={},
        )
        impact_reports = artifact_service.load_json(
            "metadata/impact_reports.json",
            default=[],
        )
        intelligence_briefs = artifact_service.load_json(
            "metadata/intelligence_briefs.json",
            default=[],
        )
        statistics = artifact_service.load_json(
            "narrative/statistics.json",
            default={},
        )

        top_narratives = sorted(
            influence_scores.items(),
            key=lambda item: item[1].get("score", 0),
            reverse=True,
        )[:10] if isinstance(influence_scores, dict) else []

        top_influencers = top_narratives[:10]

        return {
            "pipeline_status": pipeline_status,
            "executive_brief": {
                "title": executive_brief.get("title"),
                "summary": executive_brief.get("summary"),
                "highlights": executive_brief.get("highlights", [])[:5],
                "priority_narratives": executive_brief.get("priority_narratives", []),
                "emerging_risks": executive_brief.get("emerging_risks", []),
                "strategic_observations": executive_brief.get("strategic_observations", []),
            },
            "strategic_context": {
                "summary": strategic_context,
            },
            "impact_reports": impact_reports[:10] if isinstance(impact_reports, list) else [],
            "intelligence_briefs": intelligence_briefs[:10] if isinstance(intelligence_briefs, list) else [],
            "cluster_statistics": statistics if isinstance(statistics, dict) else {},
            "top_narratives": top_narratives,
            "top_influencers": top_influencers,
            "early_warnings": early_warnings[:10],
            "forecast_summary": forecasts[:10],
            "system_statistics": {
                "narrative_count": len(top_narratives),
                "warning_count": len(early_warnings),
                "forecast_count": len(forecasts),
                "timeline_points": len(timeline) if isinstance(timeline, dict) else 0,
                "influence_count": len(influence_scores) if isinstance(influence_scores, dict) else 0,
            },
        }


dashboard_service = DashboardService()