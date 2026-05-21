# Vanguard — Research-Grade Narrative Intelligence System

## Overview

Vanguard is a research-oriented AI-powered narrative intelligence and media analysis system designed to process large-scale global news streams, identify evolving narratives, cluster semantically related discourse, track narrative evolution over time, and provide explainable intelligence retrieval.

The system combines:

- Large-scale GDELT ingestion
- Parallel article extraction
- Document purification
- Semantic embeddings
- Hierarchical clustering
- Narrative abstraction
- Temporal narrative analytics
- Retrieval-Augmented Generation (RAG)

The architecture is designed for:

- Media intelligence
- Geopolitical monitoring
- OSINT systems
- Narrative tracking
- Computational journalism
- Narrative evolution research
- Trend intelligence

---

# Project Goals

## Core Objectives

Build a system capable of:

- Monitoring global narratives in real time
- Understanding narrative evolution
- Detecting emerging discourse
- Tracking narrative spikes and decay
- Creating interpretable semantic narrative clusters
- Supporting research-grade experimentation

---

# System Architecture

```text
GDELT Feed Ingestion
↓
Raw Data Lake
↓
Content Extraction Pipeline
↓
Document Purification Layer
↓
Chunking Layer
↓
Embedding Service
↓
HDBSCAN Narrative Clustering
↓
Hierarchical Subclustering
↓
Narrative Abstraction Layer
↓
FAISS Vector Database
↓
RAG Intelligence Layer
↓
Narrative Timeline Engine
↓
Future: Evaluation + Spike Detection + Narrative Evolution
```

---

# Project Structure

```text
vanguard/
│
├── analytics/
│   ├── cluster_labeler.py
│   ├── narrative_abstractor.py
│   └── timeline_engine.py
│
├── config/
│
├── data_lake/
│   ├── raw/
│   ├── raw_feeds/
│   └── processed/
│
├── embeddings/
│   └── embedding_services.py
│
├── ingestion/
│   └── gdelt_feed_ingest.py
│
├── intelligence/
│   └── rag_engine.py
│
├── pipeline/
│   └── ai_pipeline.py
│
├── processing/
│   ├── content_pipeline.py
│   ├── document_purifier.py
│   └── hdbscan_cluster.py
│
├── vectorstore/
│   └── faiss_store.py
│
└── README.md
```

---

# Phase 1 — GDELT Streaming Ingestion

## Objective

Create a scalable ingestion layer capable of continuously monitoring global media feeds.

## Features Implemented

- GDELT V2 feed ingestion
- Automatic feed downloading
- Feed deduplication tracking
- Raw feed archival
- Metadata extraction
- Incremental processing

## Technologies

- Python
- Requests
- ZIP handling
- CSV parsing
- GDELT Global Knowledge Graph (GKG)

## Output

Structured raw article metadata:

```json
{
  "date": "20260417183400",
  "source": "Reuters",
  "url": "https://..."
}
```

---

# Phase 2 — Content Extraction Pipeline

## Objective

Convert metadata-only feeds into semantically rich article content.

## Features Implemented

- Parallel extraction
- Robust extraction pipeline
- Article scraping
- Failed extraction handling
- Clean text extraction
- Enriched article generation

## Extraction Technologies

- newspaper3k
- trafilatura
- BeautifulSoup

## Output

```json
{
  "url": "...",
  "date": "20260417183400",
  "content": "Full cleaned article text..."
}
```

---

# Phase 3 — Narrative Deduplication

## Objective

Reduce redundant narrative duplication from large-scale news streams.

## Features Implemented

- Semantic reduction
- Duplicate article removal
- Narrative compression

## Results

Example reduction:

```text
20,000+ articles
↓
~1,000 unique narratives
```

## Research Importance

This phase reduces:

- embedding cost
- storage cost
- clustering noise
- retrieval contamination

---

# Phase 4 — Document Purification Layer

## Objective

Improve discourse integrity before embedding generation.

## Problem Solved

Raw web articles often contain:

- Related articles
- Recommendation blocks
- PR footers
- Contact information
- Advertisements
- Sidebar content

These create contaminated semantic representations.

## Features Implemented

- Boilerplate removal
- Noise pattern cleaning
- PR block removal
- Contact info removal
- Invalid document filtering
- Low-quality chunk rejection

## Scientific Importance

This phase improved:

- Cluster purity
- Narrative coherence
- Retrieval quality
- Timeline validity

---

# Phase 5 — Semantic Chunking Layer

## Objective

Convert large documents into semantically manageable narrative units.

## Features Implemented

- Configurable chunk size
- Metadata-aware chunk storage
- Timestamp preservation
- Chunk-level semantic processing

## Chunk Object Structure

```json
{
  "text": "chunk content...",
  "date": "20260417183400"
}
```

---

# Phase 6 — Embedding Service

## Objective

Generate semantic vector representations for narrative understanding.

## Model Used

```text
sentence-transformers/all-MiniLM-L6-v2
```

## Features Implemented

- Batch embedding generation
- Semantic representation learning
- Metadata-aware embedding pipeline

## Why Embeddings Matter

Embeddings enable:

- semantic similarity
- clustering
- retrieval
- narrative grouping
- semantic search

---

# Phase 7 — HDBSCAN Narrative Clustering

## Objective

Discover naturally emerging narratives without fixed cluster counts.

## Why HDBSCAN?

Unlike K-Means:

- no fixed K required
- detects noise automatically
- better for narrative density
- supports irregular cluster shapes

## Features Implemented

- Noise removal
- Narrative density clustering
- Adaptive semantic grouping
- Cluster filtering

## Research Benefits

HDBSCAN enables:

- cleaner narratives
- reduced hallucinated groupings
- interpretable semantic structures

---

# Phase 8 — Hierarchical Narrative Modeling

## Objective

Create multi-level narrative structures.

## Architecture

```text
Main Narrative Cluster
↓
Subcluster 1
Subcluster 2
Subcluster 3
```

## Example

```text
Middle East Conflict
├── Oil Price Impact
├── Military Escalation
└── Political Response
```

## Features Implemented

- Main narrative clustering
- Subcluster generation
- Hierarchical semantic decomposition
- Multi-level retrieval

## Research Importance

This phase enables:

- narrative decomposition
- discourse structure analysis
- granular narrative intelligence

---

# Phase 9 — Vector Database Layer

## Objective

Enable efficient semantic retrieval.

## Technology

- FAISS

## Features Implemented

- Vector indexing
- Cosine similarity retrieval
- Cluster-aware retrieval
- Metadata-aware retrieval
- Multi-cluster retrieval

## Retrieval Improvements

Implemented:

- cosine similarity search
- top-cluster retrieval
- cluster-constrained search
- semantic context retrieval

---

# Phase 10 — RAG Intelligence Layer

## Objective

Provide explainable intelligence responses grounded in retrieved narratives.

## Technologies

- Groq API
- Llama 3.1 models

## Features Implemented

- Context-grounded generation
- Retrieval-aware prompting
- Explainable context display
- Narrative-aware intelligence responses

## Important Design Principle

The system does NOT rely on:

- model memory
- hallucinated world knowledge

Instead:

- all answers are retrieval-grounded
- responses are generated from retrieved evidence

---

# Phase 11 — Narrative Abstraction Layer

## Objective

Convert semantic phrase clusters into human-readable narrative concepts.

## Pipeline

```text
Cluster Texts
↓
KeyBERT Phrase Extraction
↓
LLM Narrative Abstraction
↓
Narrative Concept Label
```

## Technologies

- KeyBERT
- Groq LLM

## Example

Raw phrases:

```text
oil prices
strait of hormuz
military retaliation
```

Narrative abstraction:

```text
US President Faces Oil Price Crisis
```

## Research Importance

This phase introduced:

- semantic concept abstraction
- interpretable narratives
- human-readable intelligence layers

---

# Phase 12 — Narrative Timeline Engine

## Objective

Track narrative evolution over time.

## Features Implemented

- Narrative frequency tracking
- Time aggregation
- Temporal narrative analysis
- Timeline visualization in console

## Example Output

```text
Narrative:
US President Faces Oil Price Crisis

2026-03-15 → 2
2026-04-17 → 5
2026-05-19 → 23
```

## Scientific Importance

Timeline analytics enables:

- narrative spikes
- narrative decay
- trend emergence
- temporal discourse analysis

---

# Retrieval Example

## Query

```text
oil prices iran israel war
```

## Retrieved Narrative

```text
US President Faces Oil Price Crisis
```

## Retrieved Context

- Strait of Hormuz closure
- Brent oil price surge
- Public response to conflict
- Energy market instability

---

# Key Research Concepts Implemented

## Semantic Narrative Modeling

Understanding narratives as semantic discourse structures.

---

## Narrative Intelligence

Tracking evolving media narratives instead of isolated articles.

---

## Temporal Narrative Analysis

Understanding how narratives evolve over time.

---

## Explainable Retrieval

Showing WHY a narrative was retrieved.

---

## Hierarchical Narrative Structure

Modeling macro and micro narratives.

---

# Current System Capabilities

## Completed Capabilities

| Capability | Status |
|---|---|
| GDELT ingestion | ✅ |
| Content extraction | ✅ |
| Deduplication | ✅ |
| Purification | ✅ |
| Chunking | ✅ |
| Embeddings | ✅ |
| HDBSCAN clustering | ✅ |
| Hierarchical narratives | ✅ |
| Vector retrieval | ✅ |
| RAG intelligence | ✅ |
| Narrative abstraction | ✅ |
| Timeline analytics | ✅ |

---

# Current Limitations

## Remaining Research Challenges

### Narrative Granularity
Some narratives remain overly broad.

### Cluster Purity
Subclusters can still mix discourse themes.

### Timeline Depth
Current timelines are count-based.

### Narrative Evolution
Narrative mutation tracking not yet implemented.

### Narrative Relationships
Cross-narrative influence modeling not implemented.

---

# Planned Future Phases

## Phase 13 — Evaluation Framework

Planned metrics:

- cluster coherence
- retrieval precision
- narrative purity
- timeline validity
- semantic consistency

---

## Phase 14 — Spike Detection Engine

Goals:

- detect sudden narrative surges
- identify emerging narratives
- identify media momentum

---

## Phase 15 — Narrative Evolution Engine

Goals:

- track narrative mutation
- detect framing changes
- monitor semantic drift

---

## Phase 16 — Narrative Graph Intelligence

Goals:

- map narrative relationships
- identify causal narratives
- detect cross-domain influence

---

## Phase 17 — Dashboard & Visualization

Planned features:

- interactive timelines
- narrative graphs
- semantic maps
- cluster exploration
- real-time dashboards

---

# Research Relevance

This project intersects with:

- Computational Journalism
- Narrative Intelligence
- OSINT Research
- Media Analytics
- NLP
- Information Retrieval
- Semantic Clustering
- Temporal Knowledge Modeling
- Discourse Analysis

---

# Technologies Used

## NLP & AI

- Sentence Transformers
- KeyBERT
- spaCy
- Groq LLM APIs

## Clustering & Retrieval

- HDBSCAN
- FAISS
- Cosine Similarity

## Data Processing

- Python
- Requests
- BeautifulSoup
- newspaper3k
- trafilatura

---

# Design Philosophy

The system prioritizes:

- interpretability
- explainability
- reproducibility
- semantic coherence
- narrative integrity
- domain independence

The system intentionally avoids:

- hardcoded narrative rules
- domain-specific heuristics
- keyword-only intelligence
- hallucination-based retrieval

---

# Conclusion

Vanguard has evolved from a basic semantic retrieval prototype into a multi-layered research-grade narrative intelligence architecture capable of:

- ingesting large-scale global media streams
- extracting semantic narratives
- clustering discourse structures
- generating interpretable narrative abstractions
- tracking narrative evolution over time
- enabling explainable narrative intelligence

The current system now forms the foundation for advanced future research into:

- narrative forecasting
- narrative evolution
- discourse dynamics
- geopolitical media intelligence
- computational journalism
- temporal semantic analysis

