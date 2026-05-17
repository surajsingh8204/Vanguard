# Project Vanguard

Predictive Narrative Tracking System

Project Vanguard ingests news feeds, enriches and clusters narratives, and powers retrieval-augmented generation (RAG) for downstream intelligence workflows. It is designed to track evolving narratives over time and support summarization, search, and analytic outputs.

## What it does

- Ingests GDELT and other feeds into a local data lake
- Extracts and enriches articles with embeddings and metadata
- Deduplicates near-duplicate narratives
- Clusters narratives for trend analysis
- Provides RAG pipelines for search and summarization
- Generates outputs like summaries, timelines, and graphs

## Architecture (high level)

- Ingestion: feed ingestion and storage in the data lake
- Processing: extraction, enrichment, deduplication
- Embeddings: vector generation and storage
- Retrieval: RAG pipelines for query-time context
- Analytics: clustering, sentiment, timeline analysis
- Outputs: summaries, article generation, visualizations

## Repository layout

- analytics/: narrative clustering, sentiment, timeline analysis
- config/: project settings and configuration
- data_lake/: raw and processed data (local only)
- embeddings/: embedding services
- ingestion/: feed ingest pipelines
- intelligence/: RAG engine
- outputs/: summary and article generation
- pipeline/: AI orchestration pipeline
- processing/: extraction, deduplication, clustering
- retrieval/: RAG pipeline
- vectorstore/: FAISS store
- visualization/: graphs and charts

## Setup

1. Create a Python environment
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Review configuration:

- See config/settings.py for defaults and environment settings

## Usage (examples)

Run ingestion or processing scripts directly:

```bash
python ingestion/gdelt_feed_ingest.py
```

Run tests:

```bash
pytest -q
```

## Data and persistence

Local data is stored under data_lake/ and is excluded from version control. The .gitignore is configured to keep raw feeds and processed data out of the repository.

## Status

Phase 1 complete.
