# Adaptive-RAG-OKF

## Implemented Platform

The project now includes a persisted enterprise knowledge and verification platform:

- PDF, DOCX, TXT, Markdown and CSV document ingestion
- Public website ingestion with SSRF protection
- SQLite document, chunk, query, claim, audit and feedback persistence
- Local hash embedding retrieval and optional Chroma compatibility
- Real RAG query endpoint with configurable OpenAI-compatible LLM providers
- Claim splitting and evidence-based claim verification
- Adaptive OKF risk evaluation
- AEVL multi-loop verification and abstention
- Evidence conflict detection and resolution
- Model-native explainability, feedback and audit history
- Premium responsive React dashboard with 12 operational pages
- Docker Compose deployment

Configure provider credentials in `.env`; never commit API keys.

A local research application for training and comparing three classifiers that estimate whether a generated answer is hallucinated:
`baseline_rag`, `self_correction`, and `adaptive_okf`. The project includes a FastAPI backend and a React + TypeScript dashboard.

> These classifiers use lightweight text/evidence features. Their scores are experimental signals, not proof that a response is factually correct.

## Project layout

- `frontend/` — Vite, React, TypeScript, and dashboard pages.
- `backend/` — FastAPI routes, data normalization, feature extraction, model training, and evaluation.
- `data/raw/` — the four supplied HaluEval-style JSONL datasets. Each line is a separate JSON object.
- `outputs/` — trained models, evaluation reports, and confusion matrices generated during training.
- `docs/` — architecture, methodology, and API reference.

## Run locally (Windows PowerShell)

### 1. Install backend dependencies

```powershell
cd backend
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

### 2. Start the API

From `backend/`, run:

```powershell
python -m uvicorn app.main:app --reload --port 8001
```

The API health check is at `http://localhost:8001/api/health`; interactive API documentation is at `http://localhost:8001/docs`. The included `frontend/.env` points the Vite API proxy to port `8001`. Change `VITE_PROXY_TARGET` there if you use another backend port.

### 3. Start the frontend

In a second terminal:

```powershell
cd frontend
npm install
npm run dev
```

Open `http://localhost:5174`. Vite proxies `/api` requests to the backend at `http://localhost:8001`. Change `VITE_PORT` in `frontend/.env` if you want to use another frontend port.

## Deploy to Vercel

The root `vercel.json` deploys the Vite frontend and FastAPI API together on one origin. Configure the Vercel project with the Supabase integration's `POSTGRES_URL`, `SUPABASE_URL`, and `SUPABASE_SERVICE_ROLE_KEY`, and connect a private Blob or Supabase Storage bucket before accepting uploads. In Vercel project settings, set `LLM_PROVIDER`, `LLM_BASE_URL`, and `LLM_MODEL` to a publicly reachable provider; never use `localhost` or `127.0.0.1` for the hosted model URL. Keep provider credentials in Vercel Environment Variables, not in source control.

The hosted function uses PostgreSQL for application records and Supabase Storage for private document files. Local Ollama, Chroma persistence, and SQLite are development-only. Hosted document uploads are limited to 4 MB by the Vercel request-body limit. Supabase Free projects may pause after inactivity.

### 4. Train and evaluate

Open **Experiments** and select **Train and evaluate**. Training uses an 80/20 stratified split with a fixed random seed and writes:

- `outputs/models/*.joblib`
- `outputs/reports/model_comparison.csv`
- `outputs/confusion_matrices/*.png`

After training, use **Analyze** to score an answer against its evidence. General-domain source records do not include evidence; their normalized evidence field is empty and they are used only as labeled examples.

## Tests

From `backend/` with the backend dependencies installed:

```powershell
python -m pytest -q
```

## API overview

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/api/health` | Backend status |
| `GET` | `/api/datasets/` | Normalized example counts by source |
| `GET` | `/api/datasets/sample?n=5` | A small normalized dataset sample |
| `POST` | `/api/experiments/train` | Train models and create the comparison report |
| `GET` | `/api/experiments/comparison` | Read model metrics |
| `POST` | `/api/analysis/` | Estimate hallucination risk for an answer |

See [API documentation](./docs/api_documentation.md), [architecture](./docs/architecture.md), and [methodology](./docs/methodology.md) for details.