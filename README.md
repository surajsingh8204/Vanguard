# Vanguard

Vanguard is a full-stack narrative-intelligence platform for ingesting global
news, extracting and cleaning article content, discovering semantic narratives,
tracking their evolution, generating forecasts and warnings, and answering
questions through retrieval-augmented generation (RAG).

The repository contains:

- a resumable GDELT-to-intelligence data pipeline;
- semantic embeddings, hierarchical HDBSCAN clustering, and a FAISS index;
- temporal, graph, influence, forecast, and evaluation analytics;
- a FastAPI API with JWT authentication and persistent conversations;
- a React intelligence dashboard and grounded AI chat interface.

## Feature showcase

Screenshots below are from a live local run of the analyst workspace after a
completed pipeline build. Metrics, labels, and timestamps change whenever the
pipeline is rebuilt from a new GDELT window.

### Intelligence Command dashboard

![Vanguard Intelligence Command dashboard](docs/images/vanguard-dashboard.png)

The dashboard summarizes pipeline health, processed documents, active
narratives, influence pressure, risk warnings, narrative share, and strategic
context in one command view.

### Grounded AI chat

![Vanguard grounded AI chat](docs/images/vanguard-chat.png)

Chat asks questions against the FAISS corpus, shows retrieval confidence,
persists conversation history, and answers with evidence grounded in indexed
narratives rather than free-form model memory.

### Narrative explorer

![Vanguard narrative explorer](docs/images/vanguard-narratives.png)

The narratives page lists discovered clusters by volume, supports label and
volume filters, and opens supporting documents plus labeled subclusters for
inspection.

### Relationship network

![Vanguard narrative network graph](docs/images/vanguard-network.png)

The network view encodes community membership by color, narrative volume by
node size, and similarity by edge weight. Hovering a node reveals influence,
volume, and connection count.

### Influence chains

![Vanguard influence chains](docs/images/vanguard-influence-chains.png)

Influence chains show which high-pressure narratives are linked to related
discourse, making cross-narrative impact easier to scan than a raw edge list.

### Temporal intelligence

![Vanguard timeline overview](docs/images/vanguard-timeline.png)

![Vanguard narrative activity chart](docs/images/vanguard-timeline-activity.png)

Timeline pages track narrative volume over time, evolution snapshots, spikes,
forecasts, and early warnings. When a corpus lands on a single calendar day,
analytics automatically fall back to hourly buckets so the charts still fill.

### Evaluation and quality

![Vanguard evaluation coherence vs purity](docs/images/vanguard-evaluation.png)

Evaluation surfaces coherence, purity, label audits, forecast hit rates, and
Vanguard-versus-baseline correlation so cluster quality can be inspected after
each rebuild.

### Generated reports

![Vanguard reports library](docs/images/vanguard-reports.png)

The reports library browses generated evaluation and intelligence artifacts,
filters by report type, and opens report contents through authenticated API
endpoints.

## Quick start: run the complete pipeline with Docker

Run these commands from the repository root:

```powershell
docker compose build pipeline
docker compose run --rm pipeline
```

Before running the complete pipeline, create a root `.env` file:

```dotenv
GROQ_API_KEY=your_groq_api_key
HF_TOKEN=
```

`HF_TOKEN` is optional for the public default embedding model. `GROQ_API_KEY`
should still be present because pipeline initialization constructs the RAG
engine even though orchestration itself does not issue a chat query. The first
build downloads Python dependencies and the first run downloads the embedding
model, so both can take longer than subsequent runs.

The pipeline runs in the foreground and prints progress to the terminal.
Persistent outputs are mounted back to the host:

```text
data_lake/                  downloaded and processed datasets
core/artifacts/             FAISS, analytics, evaluation, and report artifacts
artifacts/pipeline/         checkpoints, state, embedding batches, and logs
```

To watch the pipeline log from another PowerShell terminal:

```powershell
Get-Content artifacts/pipeline/logs/pipeline.log -Wait
```

If a run is interrupted, rerun the same Docker command. Completed work is
restored from checkpoints. After a successful run, restart the FastAPI backend
so its in-memory AI pipeline loads the new FAISS index.

## What Vanguard provides

### Intelligence pipeline

- GDELT GKG feed discovery, download, parsing, and raw archival
- Bounded ingestion and preprocessing batches
- Concurrent article download and extraction
- Trafilatura extraction with Beautiful Soup fallback
- Boilerplate purification and metadata validation
- Quality, language, and duplicate-content screening
- Sentence Transformer embeddings with per-batch checkpoints
- Main narrative clustering and hierarchical subclustering with HDBSCAN
- Human-readable cluster and subcluster labels
- Cluster-aware cosine retrieval through FAISS
- Timeline, spike, momentum, emergence, and evolution analysis
- Narrative relationship graph, communities, centrality, and influence
- Vanguard and baseline forecasts, forecast evaluation, and early warnings
- Coherence, separation, purity, and label-audit artifacts
- Intelligence briefs, impact reports, executive briefs, and strategic context
- Artifact validation before a run is marked complete

### Web application

- User registration, login, JWT sessions, and protected routes
- Intelligence dashboard with pipeline status and narrative distribution
- Narrative cluster and subcluster exploration
- Interactive narrative network with labels, volume, communities, and tooltips
- Temporal trends, spikes, forecasts, warnings, and correlation results
- Evaluation gauges and quality metrics
- Generated report browser and report-content viewer
- Grounded chat with persistent and deletable conversations
- Read-only account, client endpoint, and session information

## Architecture

```mermaid
flowchart LR
    G[GDELT GKG feeds] --> I[Ingestion]
    I --> R[Raw data lake]
    R --> E[Fetch and extract]
    E --> Q[Purify and validate]
    Q --> P[Processed articles]
    P --> M[Embeddings]
    M --> C[HDBSCAN clusters]
    C --> V[FAISS vector store]
    C --> A[Analytics and evaluation]
    A --> F[Artifact files]
    V --> B[FastAPI backend]
    F --> B
    D[(PostgreSQL)] --> B
    B --> W[React frontend]
    B --> L[Groq grounded generation]
```

The pipeline and the application runtime are intentionally separate:

- `pipeline/` coordinates long-running data and ML work.
- `core/` owns the existing ingestion, processing, modeling, retrieval, and
  analytics business logic.
- `backend/` serves artifacts, authentication, conversations, and AI queries.
- `frontend/` visualizes the API and provides the chat experience.
- PostgreSQL stores users, conversations, and messages; analytics remain
  artifact-backed.

## Repository layout

```text
vanguard/
├── backend/                 FastAPI API, auth, database models, services
├── core/
│   ├── ingestion/           GDELT feed client, parser, and raw storage
│   ├── processing/          fetch, extraction, cleaning, validation, ETL
│   ├── embeddings/          Sentence Transformer embedding service
│   ├── clustering/          HDBSCAN main and subcluster engines
│   ├── vectorstore/         FAISS vector storage and retrieval
│   ├── intelligence/        reranking, RAG, and strategic context
│   ├── analytics/           narrative, graph, forecast, and evaluation engines
│   ├── outputs/             briefs and impact reports
│   ├── pipeline/            AI build/query/analytics owner
│   └── artifacts/           generated application intelligence
├── data_lake/
│   ├── raw/                 raw article metadata batches
│   ├── raw_feeds/           downloaded GDELT feed archives
│   └── processed/           enriched article dataset
├── docs/
│   └── images/              README feature-showcase screenshots
├── docker/                  pipeline Dockerfile
├── frontend/                React, TypeScript, Vite application
├── pipeline/                resumable orchestration package and configuration
├── scripts/                 maintenance and analytics rebuild scripts
├── artifacts/pipeline/      orchestration state, checkpoints, and logs
├── compose.yaml             pipeline and PostgreSQL services
└── requirements.txt         Python environment snapshot
```

## Prerequisites

For the Docker pipeline:

- Docker Desktop with Docker Compose v2
- internet access to GDELT, article sites, Hugging Face, and Groq
- a Groq API key
- sufficient storage for feeds, model cache, embeddings, and artifacts

For the complete local application:

- Python 3.11 recommended
- Conda recommended; the project environment is named `vanguard`
- Node.js `^20.19.0` or `>=22.12.0`, plus npm
- Docker Desktop for the provided PostgreSQL service

The ML build is memory-intensive. HDBSCAN and several analytics stages operate
on the complete embedding or cluster collection in memory. Reduce
`ingestion.articles_limit` in `pipeline/config.yaml` for lower-memory machines.

## Complete application setup

### 1. Clone and enter the repository

```powershell
git clone <repository-url> vanguard
Set-Location vanguard
```

All Python and pipeline commands in this document assume the repository root as
the current directory.

### 2. Configure API keys

Create `.env` in the repository root for Docker Compose:

```dotenv
GROQ_API_KEY=your_groq_api_key
HF_TOKEN=
```

Do not commit `.env` files.

### 3. Start PostgreSQL

```powershell
docker compose up -d postgres
docker compose ps
```

Development connection details from `compose.yaml`:

```text
Host:     localhost
Port:     5432
Database: vanguard_db
User:     vanguard
Password: vanguard123
```

These credentials are for local development only.

### 4. Build intelligence artifacts

```powershell
docker compose build pipeline
docker compose run --rm pipeline
```

This step can run independently of PostgreSQL. It must finish before dashboard,
analytics, report, and chat features have a complete artifact set.

### 5. Prepare the Python environment

If the `vanguard` environment already exists:

```powershell
conda activate vanguard
```

For a new environment:

```powershell
conda create -n vanguard python=3.11 -y
conda activate vanguard
python -m pip install --upgrade pip packaging
python -c "from pathlib import Path; src=Path('requirements.txt').read_text().splitlines(); Path('requirements.local.txt').write_text('\n'.join(x for x in src if not x.startswith('packaging @ file:')) + '\n')"
python -m pip install -r requirements.local.txt
python -m pip install "python-jose[cryptography]" "passlib[bcrypt]" `
  psycopg2-binary python-multipart email-validator
Remove-Item requirements.local.txt
```

`requirements.txt` was exported from a Conda environment and currently contains
a machine-specific `packaging @ file:///...` entry. The commands above create
and install a temporary portable copy without changing the tracked file.
The pipeline Dockerfile performs the same filtering automatically.

### 6. Configure the backend

Copy the example:

```powershell
Copy-Item backend/.env.example backend/.env
```

Set at least these values in `backend/.env`:

```dotenv
APP_NAME=Vanguard Backend
APP_VERSION=0.6.0
HOST=127.0.0.1
PORT=8000
DATABASE_URL=postgresql+psycopg2://vanguard:vanguard123@localhost:5432/vanguard_db
SECRET_KEY=replace_with_a_long_random_secret
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
GROQ_API_KEY=your_groq_api_key
```

Generate a development secret with:

```powershell
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

Create the database tables:

```powershell
python -m backend.src.database.init_db
```

Start the API:

```powershell
python -m uvicorn backend.src.main:app --reload --host 127.0.0.1 --port 8000
```

Verify:

- API root: <http://127.0.0.1:8000/>
- health: <http://127.0.0.1:8000/health/>
- OpenAPI UI: <http://127.0.0.1:8000/docs>

### 7. Configure and start the frontend

In a second terminal:

```powershell
Set-Location frontend
npm install
```

The default API URL is `http://127.0.0.1:8000`. To override it, create
`frontend/.env`:

```dotenv
VITE_API_URL=http://127.0.0.1:8000
```

Start Vite:

```powershell
npm run dev
```

Open <http://127.0.0.1:5173>, register an account, and sign in.

## Docker pipeline operations

### Validate without running

```powershell
docker compose run --rm pipeline python pipeline/run_pipeline.py --dry-run
```

### Resume an interrupted run

Resume is enabled by default:

```powershell
docker compose run --rm pipeline
```

### Start a fresh run

This discards incomplete orchestration state:

```powershell
docker compose run --rm pipeline python pipeline/run_pipeline.py --no-resume
```

### Rerun from a stage

The named stage and every stage after it are rerun:

```powershell
docker compose run --rm pipeline python pipeline/run_pipeline.py --from-stage model_build
```

Valid stage names:

```text
ingestion
preprocessing
model_build
analytics_artifacts
validation
```

Examples:

```powershell
# Reprocess already-ingested batches, then rebuild everything downstream
docker compose run --rm pipeline python pipeline/run_pipeline.py --from-stage preprocessing

# Rebuild embeddings, clustering, FAISS, and analytics
docker compose run --rm pipeline python pipeline/run_pipeline.py --from-stage model_build

# Keep the model build and regenerate analytics
docker compose run --rm pipeline python pipeline/run_pipeline.py --from-stage analytics_artifacts
```

### Stop or inspect services

`docker compose run --rm pipeline` creates a one-off foreground container.
Pressing `Ctrl+C` interrupts it safely; rerun the command to resume.

```powershell
docker compose ps
docker compose logs postgres
docker compose down
```

`docker compose down` stops PostgreSQL but preserves its named volume. To avoid
accidental data loss, do not add `--volumes` unless you intend to delete the
database and model-cache volumes.

## Pipeline execution model

The orchestrator sequences existing `core` engines instead of duplicating their
business logic.

### Stage 1: ingestion

1. Generate GDELT GKG feed URLs for the configured history window.
2. Download and parse feeds.
3. deduplicate article URLs.
4. Write bounded JSON ingestion batches.
5. Stop at `ingestion.articles_limit` or when feeds are exhausted.

### Stage 2: preprocessing

1. Fetch article HTML concurrently.
2. Extract readable article text.
3. Purify document content.
4. reject low-quality, malformed, duplicate, or invalid records.
5. Append accepted records to resumable JSONL.
6. Publish `data_lake/processed/enriched_articles.json`.

### Stage 3: model build

1. Chunk accepted article content.
2. Embed chunks in configured batches.
3. Cluster embeddings with HDBSCAN.
4. subcluster and label discovered narratives.
5. Create the normalized FAISS vector index with narrative metadata.

Clustering occurs before final FAISS creation because stored vector metadata
includes cluster and subcluster IDs.

### Stage 4: analytics and artifacts

The existing `AIPipeline.run_analytics()` generates:

- timelines, spikes, emerging narratives, and evolution;
- narrative graph, communities, centrality, diagnostics, and influence;
- statistics, forecasts, baselines, hit evaluation, and early warnings;
- coherence, separation, purity, correlation, and label audits;
- intelligence briefs, impact reports, executive brief, strategic context;
- system metadata and pipeline status.

### Stage 5: validation

The run fails if a required file configured under `artifacts.required` is
missing or empty. A completed status therefore means the orchestrator validated
the expected output set.

## Pipeline configuration

Edit `pipeline/config.yaml`.

Important defaults:

| Setting | Default | Purpose |
|---|---:|---|
| `ingestion.articles_limit` | `25000` | Maximum collected articles |
| `ingestion.hours_back` | `168` | GDELT lookback window |
| `preprocessing.workers` | `10` | Fetch/extraction concurrency |
| `embeddings.model` | `all-MiniLM-L6-v2` | Sentence Transformer model |
| `embeddings.embedding_batch_size` | `64` | Model inference batch size |
| `embeddings.device` | `auto` | Sentence Transformers device |
| `vector_database.rebuild_vectors` | `true` | Force vector rebuild |
| `artifacts.rebuild_artifacts` | `true` | Force analytics rebuild |
| `pipeline.resume` | `true` | Resume incomplete work |

Both ingestion and preprocessing support automatic batch sizing. Use an
explicit integer instead of `auto` when predictable batches are required.
Supported embedding devices include `cpu`, `cuda`, and any device supported by
the installed Sentence Transformers/PyTorch build.

## Checkpoints, logs, and outputs

### Pipeline runtime state

```text
artifacts/pipeline/pipeline_state.json
artifacts/pipeline/logs/pipeline.log
artifacts/pipeline/ingestion/batch_*.json
artifacts/pipeline/preprocessing/accepted_articles.jsonl
artifacts/pipeline/embeddings/batch_*.npy
artifacts/pipeline/embeddings/manifest.json
```

The state file is written atomically. A stage failure records the stage and
error, logs the traceback, exits non-zero, and leaves completed checkpoints for
the next run.

### Application artifacts

Key generated files include:

```text
core/artifacts/vectorstore/faiss.index
core/artifacts/vectorstore/metadata.json
core/artifacts/narrative/clusters.json
core/artifacts/narrative/cluster_labels.json
core/artifacts/narrative/statistics.json
core/artifacts/narrative/timeline.json
core/artifacts/narrative/emerging.json
core/artifacts/narrative/forecasts.json
core/artifacts/narrative/early_warnings.json
core/artifacts/graphs/nodes.json
core/artifacts/graphs/edges.json
core/artifacts/evaluation/coherence.json
core/artifacts/evaluation/purity.json
core/artifacts/evaluation/forecast_evaluation.json
core/artifacts/evaluation/correlation.json
core/artifacts/metadata/executive_brief.json
core/artifacts/metadata/pipeline_status.json
```

The API reads these artifacts to populate the frontend.

## Backend and API

The FastAPI backend uses bearer JWT authentication. With the exception of the
root, health, registration, and login routes, application endpoints require:

```http
Authorization: Bearer <access_token>
```

### Endpoint overview

| Method | Endpoint | Purpose |
|---|---|---|
| `GET` | `/health/` | Service health |
| `POST` | `/auth/register` | Create an account |
| `POST` | `/auth/login` | Obtain an access token |
| `GET` | `/auth/me` | Current account |
| `GET` | `/dashboard/` | System and executive summary |
| `GET` | `/narrative/summary` | Narrative aggregate data |
| `GET` | `/narrative/clusters` | Paginated/filterable clusters |
| `GET` | `/graphs/summary` | Graph metrics |
| `GET` | `/graphs/network` | Paginated/filterable nodes and edges |
| `GET` | `/temporal/timeline` | Timeline, spikes, forecasts, warnings |
| `GET` | `/evaluation/summary` | Evaluation and correlation results |
| `GET` | `/reports/latest` | Latest generated reports |
| `GET` | `/reports/history` | Report listing using the history contract |
| `GET` | `/reports/content` | Safe report-content lookup |
| `POST` | `/query/` | Grounded AI query and message persistence |
| `POST` | `/conversations/` | Create a conversation |
| `GET` | `/conversations/` | List the current user's conversations |
| `GET` | `/conversations/{id}` | Load a conversation and messages |
| `PATCH` | `/conversations/{id}` | Rename a conversation |
| `DELETE` | `/conversations/{id}` | Remove a conversation |

Analytics endpoints return `{status, generated_at, data, error?}` envelopes.
Authentication, query, and conversation endpoints return their response models
directly. `/reports/history` currently returns the same listing shape as
`/reports/latest`. Conversation rename is available through the API; the current
chat UI exposes create, open, and delete.

Use `/docs` for complete schemas and interactive requests.

## Chat and RAG flow

![Grounded chat with retrieval confidence](docs/images/vanguard-chat.png)

1. The frontend sends the question and optional conversation ID to `/query/`.
2. The backend creates or loads the authenticated user's conversation.
3. The question is embedded and searched globally in FAISS.
4. The pipeline selects relevant clusters and performs cluster-local search.
5. Retrieved chunks are enriched, reranked, and diversified by subcluster.
6. Low-confidence retrieval is rejected instead of forcing an answer.
7. Groq generates an answer from the retrieved evidence and strategic context.
8. User and assistant messages are persisted in PostgreSQL.

The backend lazily creates an in-memory `AIPipeline` singleton. If the pipeline
publishes a new vector index while the API is running, restart the API before
issuing new chat queries.

## Frontend pages

| Route | Feature | Screenshot |
|---|---|---|
| `/login`, `/register` | Authentication and account creation | — |
| `/dashboard` | Pipeline health, volumes, influence, risks, executive brief | `docs/images/vanguard-dashboard.png` |
| `/chat` | RAG chat, conversation history, and conversation deletion | `docs/images/vanguard-chat.png` |
| `/narratives` | Cluster, label, volume, and subcluster exploration | `docs/images/vanguard-narratives.png` |
| `/graph` | Interactive narrative relationship network and influence chains | `docs/images/vanguard-network.png`, `docs/images/vanguard-influence-chains.png` |
| `/timeline` | Temporal evolution, forecasts, warnings, and correlations | `docs/images/vanguard-timeline.png`, `docs/images/vanguard-timeline-activity.png` |
| `/evaluation` | Cluster and forecast quality metrics | `docs/images/vanguard-evaluation.png` |
| `/reports` | Generated report listing and content viewer | `docs/images/vanguard-reports.png` |
| `/settings` | Read-only profile, API endpoint, and logout | — |

See [Feature showcase](#feature-showcase) for the full illustrated gallery.

The Vite development server binds to `http://127.0.0.1:5173`. The client stores
the JWT access token in browser `localStorage`, attaches it to API requests, and
redirects to login after a `401` response. There is no settings-update API.

## Development commands

### Pipeline without Docker

```powershell
conda activate vanguard
python pipeline/run_pipeline.py
python pipeline/run_pipeline.py --dry-run
python pipeline/run_pipeline.py --from-stage model_build
python pipeline/run_pipeline.py --no-resume
```

### Backend

```powershell
conda activate vanguard
python -m backend.src.database.init_db
python -m uvicorn backend.src.main:app --reload
```

### Frontend

```powershell
Set-Location frontend
npm run dev
npm run lint
npm run build
npm run preview
```

### Tests

The orchestration tests use Python's built-in `unittest`:

```powershell
conda activate vanguard
python -m unittest pipeline.tests.test_orchestrator -v
```

## Common operations

### Rebuild analytics from existing clustered data

```powershell
conda activate vanguard
python scripts/rebuild_analytics.py
```

### Change the corpus size

Edit:

```yaml
ingestion:
  articles_limit: 5000
```

Then begin a new run or rerun from ingestion:

```powershell
docker compose run --rm pipeline python pipeline/run_pipeline.py --no-resume
```

### Use CPU explicitly

```yaml
embeddings:
  device: cpu
```

### Use an NVIDIA GPU

Set `embeddings.device: cuda` only when the container or local environment has a
CUDA-enabled PyTorch build and GPU access. The current Compose service does not
declare GPU devices by default.

## Troubleshooting

### `GROQ_API_KEY` is missing

Add the key to root `.env` for Docker and `backend/.env` for the API. Recreate
the one-off pipeline container by rerunning `docker compose run --rm pipeline`.

### PostgreSQL connection fails

Check:

```powershell
docker compose ps
docker compose logs postgres
```

Confirm `DATABASE_URL` uses `localhost:5432` when the backend runs on the host.
The hostname would be `postgres` only for another container on the Compose
network.

### Authentication modules are missing

Install the backend-specific runtime packages:

```powershell
python -m pip install "python-jose[cryptography]" "passlib[bcrypt]" `
  psycopg2-binary python-multipart email-validator
```

### Dashboard or reports are empty

Confirm the pipeline completed and
`core/artifacts/metadata/pipeline_status.json` exists. Inspect
`artifacts/pipeline/logs/pipeline.log`, then rerun the failed stage.

### Chat uses an old index

Restart Uvicorn after every successful pipeline model rebuild. Artifact-backed
dashboard routes can reread changed files, but chat keeps the AI pipeline and
FAISS index in memory.

### Pipeline container exits

Read the final terminal error and:

```powershell
Get-Content artifacts/pipeline/logs/pipeline.log -Tail 200
Get-Content artifacts/pipeline/pipeline_state.json
```

Correct the underlying network, key, resource, or data problem and rerun the
same command to resume.

### Out of memory during model build

Reduce `ingestion.articles_limit` and `embeddings.embedding_batch_size`. The
embedding batch setting controls inference memory, while clustering and some
evaluation stages still require full in-memory collections.

### Frontend cannot reach the API

Verify:

- Uvicorn is listening on `127.0.0.1:8000`;
- `VITE_API_URL` matches that address;
- the frontend runs on `localhost:5173` or `127.0.0.1:5173`, which are the
  configured CORS origins;
- the browser token is current.

## Public repository checklist

Before publishing a fork or deployment:

1. Copy `.env.example` and `backend/.env.example` to local `.env` files; never
   put real values in the examples.
2. Confirm `git status --ignored` marks local `.env` files, data-lake content,
   FAISS indexes, model checkpoints, logs, databases, and frontend build output
   as ignored.
3. Review staged files before committing. Generated intelligence can contain
   source-derived text and should not be pushed by default.
4. If a secret was ever committed, rotate it and purge the file from Git
   history before making the repository public. Adding a path to `.gitignore`
   does not remove it from earlier commits.
5. Enable GitHub secret scanning and push protection for the repository.

The repository keeps only `.gitkeep` placeholders for runtime data directories.
Running the pipeline regenerates the excluded files locally.

## Operational and security notes

- The root Compose file currently containerizes the pipeline and PostgreSQL.
  The FastAPI backend and React frontend run locally using the commands above.
- Database tables are created with SQLAlchemy `create_all`; there is no Alembic
  migration chain yet.
- Docker mounts `data_lake/`, `core/artifacts/`, and `artifacts/`, but not
  `evaluation_logs/`. Timestamped evaluation snapshots written inside a
  `--rm` container are discarded when the container exits.
- Change PostgreSQL credentials and `SECRET_KEY` before any non-development
  deployment.
- Keep Groq and Hugging Face tokens outside source control.
- Review scraping permissions, source terms, rate limits, and data-retention
  requirements before production use.
- Generated artifacts and data-lake contents can be large and may contain
  source-derived text.
- The pipeline is resumable, but core clustering and analytics are not fully
  incremental; a model-stage failure can require substantial recomputation.
- FAISS uses an exact flat index, so search and memory costs grow with the
  corpus.
- Forecasts and early warnings are analytical signals, not verified facts or
  operational decisions.

## Technology stack

- **Data and ML:** Python, GDELT, Requests, Trafilatura, Beautiful Soup,
  Sentence Transformers, PyTorch, HDBSCAN, scikit-learn, NumPy
- **Retrieval and generation:** FAISS, Groq, Llama 3.1
- **Analytics:** NetworkX, temporal statistics, forecasting and evaluation
  engines
- **Backend:** FastAPI, SQLAlchemy, PostgreSQL, JWT
- **Frontend:** React 19, TypeScript, Vite, TanStack Query, ECharts, Recharts,
  Cytoscape, Framer Motion, Tailwind CSS
- **Operations:** Docker Compose, resumable JSON/JSONL/NumPy checkpoints,
  rotating logs

For lower-level orchestration details, see
[`pipeline/README.md`](pipeline/README.md).
