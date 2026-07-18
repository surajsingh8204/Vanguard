# Vanguard Frontend

React + TypeScript intelligence UI for the Vanguard FastAPI backend.

## Stack

- Vite + React 19 + TypeScript
- Tailwind CSS 4
- TanStack Query + Axios
- Recharts + ECharts
- Cytoscape (knowledge graph)
- Framer Motion

## Setup

```bash
conda activate vanguard
cd frontend
npm install
npm run dev
```

App: http://127.0.0.1:5173  
API (default): http://127.0.0.1:8000

Configure API URL in `.env`:

```
VITE_API_URL=http://127.0.0.1:8000
```

## Backend

Start the API from the repo root with the `vanguard` conda env so imports resolve:

```bash
conda activate vanguard
cd S:\projects\vanguard
uvicorn backend.src.main:app --reload --host 127.0.0.1 --port 8000
```

## Routes

| Path | Backend |
|------|---------|
| `/login`, `/register` | `/auth/*` |
| `/dashboard` | `GET /dashboard/` |
| `/chat` | `/query/`, `/conversations/` |
| `/narratives` | `/narrative/*` |
| `/graph` | `/graphs/*` |
| `/timeline` | `/temporal/timeline` |
| `/evaluation` | `/evaluation/summary` |
| `/reports` | `/reports/*` |
| `/settings` | `/auth/me` |
