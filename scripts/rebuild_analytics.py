"""Rebuild analytics artifacts from cached clustering results.

Reuses the existing vector store and clustered chunks (no re-embedding or
re-clustering) and regenerates every analytics artifact: timeline, spikes,
emerging narratives, forecasts, early warnings, evaluations, graphs,
briefs, and strategic context.

Usage:
    python scripts/rebuild_analytics.py
"""

import json
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.pipeline.ai_pipeline import AIPipeline


def main():
    pipeline = AIPipeline()

    with open(
        "data_lake/processed/enriched_articles.json",
        "r",
        encoding="utf-8",
    ) as f:
        articles = json.load(f)

    # Uses the cached vector store / clusters when the dataset is unchanged.
    pipeline.build_vector_db(articles)

    pipeline.run_analytics(force_rebuild=True)

    print("\n✅ Analytics artifacts rebuilt.")


if __name__ == "__main__":
    main()
