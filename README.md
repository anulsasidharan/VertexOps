# VertexOps

An end-to-end LLMOps platform for deploying, monitoring, and fine-tuning generative AI applications. Built with FastAPI and Google Cloud Vertex AI, VertexOps integrates Retrieval-Augmented Generation (RAG), vector search, and CI/CD pipelines for production-grade GenAI management.

---

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Project Status](#project-status)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Quick Start — Docker](#quick-start--docker)
- [Quick Start — Local (no Docker)](#quick-start--local-no-docker)
- [Database Migrations](#database-migrations)
- [Running Tests](#running-tests)
- [Environment Variables](#environment-variables)
- [API Reference](#api-reference)
- [Documentation](#documentation)

---

## Overview

VertexOps gives ML engineers and DevOps teams a single control plane for the full GenAI lifecycle:

| Capability | Description |
|---|---|
| **Model Deployment** | Deploy and version LLMs via Vertex AI or OpenAI-compatible endpoints |
| **RAG Pipeline** | Document ingestion, chunking, embedding, and retrieval-augmented generation |
| **Vector Search** | Namespace-aware upsert and similarity search (Pinecone / Vertex Matching Engine) |
| **Experiment Tracking** | Run experiments, compare configs, and record evaluation metrics |
| **Monitoring** | Request latency, error rates, token usage, and cost tracking |
| **CI/CD** | Automated model testing, validation, and deployment via Cloud Build / GitHub Actions |

---

## Architecture

```
[API Client]
     │
[FastAPI API Gateway]  ─── JWT / API Key auth
     │
     ├── [Ingestion Service]  →  [Chunking]  →  [Embedding]  →  [Vector Store]
     │
     ├── [Retrieval Service]  ←─────────────────────────────────────────────┘
     │
     ├── [Generation Service]  →  [LLM Provider (OpenAI / Vertex AI)]
     │
     ├── [Experiment Registry]  →  [Evaluation Service]  →  [MLflow / W&B]
     │
     └── [Monitoring & Logging]  →  [GCP Cloud Monitoring / Prometheus]

[Celery Workers]  ←  Redis Broker  →  [PostgreSQL Metadata Store]
```

**Key design decisions:**

- **GCP-first:** Vertex AI, GCS, and Cloud Monitoring are the primary cloud targets; other providers are abstracted behind interfaces.
- **Async throughout:** SQLAlchemy 2.0 with `asyncpg`, FastAPI async handlers, and Celery for background jobs.
- **Repository pattern:** Each domain aggregate has a typed repository; routers call services, services call repositories — never the reverse.
- **Provider-agnostic interfaces:** Embedding, vector store, and LLM providers are swappable via environment config.

---

## Tech Stack

| Layer | Technology |
|---|---|
| API & Backend | Python 3.11+, FastAPI, Uvicorn, **uv** (dependency lock + virtualenv) |
| Database | PostgreSQL 16, SQLAlchemy 2.0 (async), Alembic |
| Cache & Broker | Redis 7 |
| Background Workers | Celery |
| LLM Management | Google Cloud Vertex AI, OpenAI, LangChain |
| Vector Store | Pinecone, Vertex Matching Engine |
| Object Storage | Google Cloud Storage (local fallback for dev) |
| Authentication | JWT (HS256), API Keys |
| Observability | Prometheus, OpenTelemetry, GCP Cloud Logging |
| CI/CD | GitHub Actions, Google Cloud Build |
| Containerisation | Docker, Docker Compose |

---

## Project Status

| Phase | Goal | Status |
|---|---|---|
| **Phase 1** | Repository skeleton, config, local infra, logging | **Complete** |
| **Phase 2** | DB engine, session management, schema models, JWT + API key auth, RBAC, rate limiting | **Complete** |
| **Phase 3** | Ingestion and indexing pipeline — storage, Documents API, parsing, chunking, embedding, vector store, index management, Celery workers, and end-to-end async pipeline | **Complete** |
| **Phase 4** | Retrieval, hybrid search, generation, query API, realtime streaming, citations, and guardrails | **Complete** |
| **Phase 5** | Experiments, evaluation, MLflow tracking, and LangGraph optimization orchestrator | **Complete** |
| **Phase 6** | Frontend dashboard, query playground, eval views, SendGrid/Twilio notifications, Stripe billing hooks | **Complete** |
| **Phase 7** | Prometheus metrics, OTel tracing, audit logging, production Docker targets, GCP Cloud Run manifests, Cloud Build pipeline, GitHub Actions CI/CD, AWS parity Terraform | **Complete** |
| Phase 8 | Final quality sweep and documentation | Planned |

---

## Project Structure

```
vertexops/
├── backend/
│   ├── main.py                  # FastAPI app factory and lifespan hooks
│   ├── api/
│   │   └── v1/                  # Route handlers (health, documents, indexes, …)
│   ├── core/
│   │   ├── config.py            # Pydantic-settings typed configuration
│   │   ├── db.py                # Async engine, session factory, get_db dependency
│   │   ├── exceptions.py        # Domain exception hierarchy and error envelopes
│   │   ├── logging.py           # Structured JSON logging
│   │   └── middleware/          # Request context, error handler middleware
│   ├── models/                  # SQLAlchemy ORM models (Base, Workspace, User, Document, Chunk, …)
│   ├── repositories/            # Typed async repositories per aggregate
│   ├── ingestion/               # Document loading, parsing, deduplication
│   ├── chunking/                # Chunking strategy registry
│   ├── embedding/               # Embedding provider interface and adapters
│   ├── vector_store/            # Vector store interface and provider adapters
│   ├── retrieval/               # Retrieval service (vector + hybrid search)
│   ├── generation/              # Generation service, prompt templates
│   ├── evaluation/              # Eval dataset service, metric aggregation
│   ├── experiments/             # Experiment registry and MLflow tracking bridges
│   ├── orchestration/           # LangGraph-backed optimization orchestrator
│   ├── integrations/            # Optional external adapters (SendGrid, Twilio, Stripe)
│   └── workers/                 # Celery app and task definitions
├── alembic/                     # Database migrations
│   └── versions/                # Migration scripts (0001_workspaces_and_users, …)
├── tests/
│   ├── unit/                    # Unit tests with mocked dependencies
│   └── integration/             # Integration tests against live services
├── docs/                        # Architecture, API spec, DB schema, and deployment docs
├── frontend/                    # React/Vite dashboard (login, documents, indexes, query playground, evaluations)
├── docker-compose.yml           # Local dev: API, PostgreSQL, Redis, Worker
├── Dockerfile                   # Multi-stage build (uv export + wheels + runtime)
├── pyproject.toml               # Runtime + dev dependency declarations (PEP 621), tooling config
└── uv.lock                      # Locked dependency tree (uv); commit with pyproject changes
```

---

## Prerequisites

- Python 3.11+
- **[uv](https://docs.astral.sh/uv/)** (recommended) — install: `pip install uv` or see [Installing uv](https://docs.astral.sh/uv/getting-started/installation/)
- Docker and Docker Compose (for local infra)
- `git`

Optional (for cloud features):
- `gcloud` CLI configured with a GCP project
- OpenAI API key
- Pinecone API key

---

## Quick Start — Docker

The fastest way to run the full stack locally:

```bash
# 1. Clone the repository
git clone https://github.com/your-org/vertexops.git
cd vertexops

# 2. Copy the environment template
cp .env.example .env
# Edit .env — at minimum set JWT_SECRET_KEY and API_KEY_PEPPER

# 3. Start backing services (PostgreSQL + Redis)
docker compose up -d postgres redis

# 4. Run database migrations
docker compose run --rm api alembic upgrade head

# 5. Start the API
docker compose up -d api

# 6. Verify it's running
curl http://localhost:8000/api/v1/health
# → {"status":"ok"}

curl http://localhost:8000/api/v1/ready
# → {"status":"ok","checks":{"database":"ok"}}
```

To also start the background worker:

```bash
docker compose --profile worker up -d worker
```

---

## Quick Start — Local (no Docker)

Run the API against a local or remote PostgreSQL and Redis instance:

```bash
# 1. Install dependencies into .venv (runtime + dev/test tools)
uv sync --all-groups

# 2. Configure environment
cp .env.example .env
# Edit .env with your DATABASE_URL, REDIS_URL, JWT_SECRET_KEY, API_KEY_PEPPER

# 3. Apply migrations
uv run alembic upgrade head

# 4. (Optional) Create a local dev admin for the dashboard JWT login — only when APP_ENV=development
# Run from this repository root (where alembic.ini lives), not from frontend/
uv run python -m scripts.bootstrap_dev_user
# Defaults: admin@localhost / changeme (override with --email / --password)
# From frontend/: npm run db:migrate   and   npm run db:bootstrap-user -- --email ... --password ...

# 5. Start the API (development mode with auto-reload)
uv run uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

**Runtime only** (no linters/test tools): `uv sync` (omit `--all-groups`).

**After changing dependencies** in `pyproject.toml`: run `uv lock` and commit the updated `uv.lock`. In CI, `uv lock --check` fails if the lockfile is stale.

API docs are available at [http://localhost:8000/docs](http://localhost:8000/docs) in development mode.

**PostgreSQL not running?** `ConnectionRefusedError` from `alembic` or `bootstrap_dev_user` means nothing is listening on the host/port in `DATABASE_URL`. From the repo root, start the bundled database:

```bash
docker compose up -d postgres
```

Set `DATABASE_URL` in `.env` to match that server. For the Compose service in this repository, the host connection string is:

`postgresql+asyncpg://vertexops:vertexops@localhost:5432/vertexops`

(If you use a different local Postgres, keep user/password/db name in the URL in sync with that instance.)

---

## Database Migrations

Migrations are managed with Alembic and live in `alembic/versions/`.

```bash
# Apply all pending migrations
uv run alembic upgrade head

# Roll back one migration
uv run alembic downgrade -1

# Auto-generate a new migration from model changes
uv run alembic revision --autogenerate -m "describe your change"

# Show current migration state
uv run alembic current

# Show migration history
uv run alembic history
```

### Current migrations

| Revision | Description |
|---|---|
| `0001` | Create `workspaces` and `users` tables |
| `0002` | Create `documents` and `chunks` tables |
| `0003` | Create `indexes`, `experiments`, `runs`, `eval_cases`, `metric_snapshots`, and `deployments` tables |
| `0004` | Create `api_keys` table |

---

## Running Tests

```bash
# All unit tests
uv run pytest tests/unit/

# All tests (requires running PostgreSQL and Redis for integration tests)
uv run pytest

# With coverage report
uv run pytest --cov=backend --cov-report=term-missing

# A specific test file
uv run pytest tests/unit/test_db.py -v
```

The test suite uses `pytest-asyncio` in auto mode. Required environment variables are set automatically in `tests/conftest.py` — no `.env` file is needed for unit tests.

---

## Environment Variables

Copy `.env.example` to `.env` and configure the values below. Variables marked **REQUIRED** must be set before the app will start.

| Variable | Required | Default | Description |
|---|---|---|---|
| `APP_ENV` | | `development` | `development`, `staging`, or `production` |
| `DEBUG` | | `false` | Enable SQLAlchemy query logging |
| `DATABASE_URL` | | `postgresql+asyncpg://postgres:postgres@localhost:5432/vertexops` | Async PostgreSQL connection string |
| `REDIS_URL` | | `redis://localhost:6379/0` | Redis connection string |
| `JWT_SECRET_KEY` | **REQUIRED** | — | Secret for signing JWTs (`openssl rand -hex 32`) |
| `API_KEY_PEPPER` | **REQUIRED** | — | Pepper for API key hashing (`openssl rand -hex 16`) |
| `OPENAI_API_KEY` | | — | Required when using OpenAI embeddings or chat |
| `GCP_PROJECT_ID` | | — | Required when using Vertex AI or GCS |
| `PINECONE_API_KEY` | | — | Required when using Pinecone as the vector store |
| `LOG_LEVEL` | | `INFO` | `DEBUG`, `INFO`, `WARNING`, `ERROR`, or `CRITICAL` |

See `.env.example` for the full list including all Vertex AI, storage, and observability options.

---

## API Reference

All routes are served under `/api/v1`.

### Currently implemented

| Method | Path | Description |
|---|---|---|
| `GET` | `/api/v1/health` | Liveness probe — always returns `200 OK` |
| `GET` | `/api/v1/ready` | Readiness probe — checks database connectivity |
| `POST` | `/api/v1/auth/token` | Issue JWT access token (email + password) |
| `POST` | `/api/v1/auth/api-keys` | Create API key for the authenticated user |
| `GET` | `/api/v1/auth/api-keys` | List API keys for the authenticated user |
| `DELETE` | `/api/v1/auth/api-keys/{key_id}` | Revoke an API key |
| `POST` | `/api/v1/documents` | Register a document (metadata only) |
| `POST` | `/api/v1/documents/upload-url` | Get a pre-signed upload URL for a document |
| `POST` | `/api/v1/documents/{id}/complete` | Mark a document upload as complete |
| `GET` | `/api/v1/documents` | List documents in the workspace (paginated) |
| `GET` | `/api/v1/documents/{id}` | Retrieve a single document |
| `DELETE` | `/api/v1/documents/{id}` | Delete a document and its storage object |
| `POST` | `/api/v1/indexes` | Create a vector index |
| `GET` | `/api/v1/indexes` | List indexes |
| `GET` | `/api/v1/indexes/{id}` | Retrieve index details |
| `POST` | `/api/v1/indexes/{id}/rebuild` | Trigger index rebuild |
| `POST` | `/api/v1/query` | RAG query with source citations and latency |
| `POST` | `/api/v1/experiments` | Create an experiment |
| `GET` | `/api/v1/experiments` | List experiments |
| `GET` | `/api/v1/experiments/{id}` | Retrieve experiment details |
| `POST` | `/api/v1/experiments/{id}/run` | Kick off an experiment run |
| `POST` | `/api/v1/evaluations` | Start an evaluation job |
| `GET` | `/api/v1/evaluations/{id}` | Retrieve evaluation status |
| `GET` | `/api/v1/evaluations/{id}/report` | Download evaluation report artifact |

### Planned endpoints (see `docs/API_SPEC.md`)

| Group | Prefix | Description |
|---|---|---|
| Metrics | `/metrics` | Prometheus metrics endpoint (Phase 7) |

Error responses follow a consistent envelope:

```json
{
  "error": {
    "code": "NOT_FOUND",
    "message": "Document not found",
    "details": {},
    "timestamp": "2026-04-17T10:00:00Z"
  }
}
```

---

## Documentation

Detailed specifications live in the `docs/` directory:

| Document | Description |
|---|---|
| [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) | High-level and module-level architecture |
| [`docs/API_SPEC.md`](docs/API_SPEC.md) | Full REST API specification with request/response schemas |
| [`docs/DB_SCHEMA.md`](docs/DB_SCHEMA.md) | PostgreSQL metadata schema and ER diagram |
| [`docs/LDL.md`](docs/LDL.md) | Low-level design: module boundaries, route groups, service layer |
| [`docs/HDL.md`](docs/HDL.md) | High-level design |
| [`docs/DEPLOYMENT.md`](docs/DEPLOYMENT.md) | GCP deployment guide and environment templates |
| [`docs/PRD.md`](docs/PRD.md) | Product requirements document |
| [`task.md`](task.md) | Implementation roadmap and task tracking |

---

## Contributing

Branch flow: `main ← development ← feature/*`

1. Branch from `development`: `git checkout -b feature/your-feature`
2. Implement with tests (target >80% coverage for touched modules)
3. Ensure `pytest` and `ruff check .` pass locally
4. Open a pull request against `development`
5. Pass CI checks and code review before merge

Code style is enforced by `ruff` (PEP 8, import sorting). Type checking via `mypy`. See `pyproject.toml` for configuration.

---

## License

Specify your license here.
