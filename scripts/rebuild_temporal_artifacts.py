"""Rebuild temporal/forecast/evaluation artifacts without re-embedding.

Uses the current clustered_chunks and influence scores already on disk, so a
single-day GDELT window can be re-bucketed into hours and the Timeline /
Evaluation pages populate without a full pipeline rerun.

Usage:
    python scripts/rebuild_temporal_artifacts.py
"""

from __future__ import annotations

import json
import math
import os
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)

from core.analytics.evaluation.correlation_evaluator import CorrelationEvaluator
from core.analytics.evaluation.forecast_evaluator import ForecastEvaluator
from core.analytics.narrative.early_warning_engine import EarlyWarningEngine
from core.analytics.narrative.emerging_narrative_detector import EmergingNarrativeDetector
from core.analytics.narrative.evolution_engine import EvolutionEngine
from core.analytics.narrative.forecast_engine import ForecastEngine
from core.analytics.narrative.spike_detector import SpikeDetector
from core.analytics.narrative.timeline_engine import TimelineEngine
from core.outputs.reports.executive_brief import ExecutiveBriefGenerator
from core.outputs.reports.intelligence_brief import IntelligenceBriefGenerator
from core.intelligence.strategic_context_builder import StrategicContextBuilder
from core.utils.artifact_manager import ArtifactManager


def _load(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def _json_safe(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: _json_safe(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_json_safe(item) for item in value]
    if isinstance(value, float) and not math.isfinite(value):
        return None
    return value


def main() -> int:
    artifacts = ROOT / "core" / "artifacts"
    manager = ArtifactManager()

    clustered_chunks = _load(artifacts / "clustered_chunks.json", [])
    cluster_labels_raw = _load(artifacts / "cluster_labels.json", {})
    influence_scores = _load(artifacts / "analytics" / "influence_scores.json", {})
    if not influence_scores:
        influence_scores = _load(artifacts / "graphs" / "influencers.json", {})

    if not clustered_chunks or not cluster_labels_raw:
        print("Missing clustered_chunks.json or cluster_labels.json")
        return 1

    cluster_labels = {
        int(key): value for key, value in cluster_labels_raw.items()
    }

    timeline_engine = TimelineEngine()
    timeline = timeline_engine.build(clustered_chunks, cluster_labels)
    print(
        f"Timeline resolution={timeline_engine.resolution} "
        f"narratives={len(timeline)} "
        f"max_buckets={max((len(v) for v in timeline.values()), default=0)}"
    )

    spikes = SpikeDetector().detect(timeline)
    emerging = EmergingNarrativeDetector().detect(spikes)

    evolution_engine = EvolutionEngine()
    temporal = evolution_engine.build_temporal_clusters(
        clustered_chunks,
        cluster_labels,
    )
    evolution = evolution_engine.detect_evolution(temporal)
    print(
        f"Evolution resolution={evolution_engine.resolution} "
        f"narratives={len(evolution)}"
    )

    forecast_engine = ForecastEngine()
    forecasts = forecast_engine.forecast(timeline, influence_scores, emerging)
    baseline = forecast_engine.baseline_forecast(timeline)
    warnings = EarlyWarningEngine().generate(forecasts)

    forecast_evaluation = ForecastEvaluator().evaluate(
        timeline,
        baseline,
        forecasts,
    )
    correlation = CorrelationEvaluator().evaluate(
        timeline,
        baseline,
        forecasts,
    )

    impact_reports = _load(artifacts / "metadata" / "impact_reports.json", [])
    executive_brief = ExecutiveBriefGenerator().generate(
        forecasts,
        warnings,
        influence_scores,
        impact_reports,
    )
    strategic_context = StrategicContextBuilder().build(
        forecasts,
        warnings,
        influence_scores,
        impact_reports,
    )

    # Prefer the existing graph for intelligence briefs; fall back to a stub.
    try:
        import networkx as nx

        edges = _load(artifacts / "graphs" / "edges.json", [])
        nodes = _load(artifacts / "graphs" / "nodes.json", [])
        graph = nx.Graph()
        for node in nodes:
            graph.add_node(node.get("id"), **{k: v for k, v in node.items() if k != "id"})
        for edge in edges:
            graph.add_edge(
                edge.get("source"),
                edge.get("target"),
                weight=float(edge.get("weight", 0) or 0),
            )
        intelligence_briefs = IntelligenceBriefGenerator().generate(
            forecasts,
            influence_scores,
            warnings,
            graph,
        )
    except Exception as exc:
        print(f"Skipping intelligence briefs rebuild: {exc}")
        intelligence_briefs = _load(
            artifacts / "metadata" / "intelligence_briefs.json",
            [],
        )

    outputs = {
        "narrative/timeline.json": timeline,
        "analytics/timeline.json": timeline,
        "narrative/spikes.json": spikes,
        "narrative/emerging.json": emerging,
        "narrative/evolution.json": evolution,
        "narrative/forecasts.json": forecasts,
        "analytics/forecasts.json": forecasts,
        "narrative/early_warnings.json": warnings,
        "analytics/early_warnings.json": warnings,
        "evaluation/forecast_evaluation.json": forecast_evaluation,
        "evaluation/correlation.json": correlation,
        "metadata/intelligence_briefs.json": intelligence_briefs,
        "metadata/executive_brief.json": executive_brief,
        "analytics/executive_brief.json": executive_brief,
        "metadata/strategic_context.json": strategic_context,
        "analytics/strategic_context.json": strategic_context,
    }

    for relative, payload in outputs.items():
        manager.save_json(
            str(artifacts / relative),
            _json_safe(payload),
        )
        print(f"saved {relative}")

    print("\nTemporal artifacts rebuilt.")
    print(
        "forecasts=",
        len(forecasts),
        "warnings=",
        len(warnings),
        "spikes=",
        len(spikes),
        "evolution=",
        len(evolution),
        "corr=",
        correlation,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
