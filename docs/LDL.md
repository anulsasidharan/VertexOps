# VertexOps — Low-Level Design (LDL)

> **Specification:** Concrete module boundaries, API route groups, and background job concerns for **VertexOps**. Paths are **prescriptive** — align implementation to this document over time. Complements [HDL.md](HDL.md) and [ARCHITECTURE.md](ARCHITECTURE.md).

---

## 1. API application entry (target)

| Item | Location (example) | Notes |
|------|--------------------|-------|
| ASGI application | `backend/app/main.py` or `src/api/main.py` | Creates FastAPI app, mounts routers |
| Settings | `core/config.py` | `pydantic-settings`; single `get_settings()` |
| Lifespan | app factory | Init DB pool, Redis if used, telemetry |
| Routers | `api/v1/*.py` | Mounted under `/api/v1` |

---

## 2. HTTP middleware (recommended order)

Outermost to innermost (exact framework order follows Starlette/FastAPI registration rules):

1. **CORS** — allowlist origins from settings
2. **Rate limiting** — per IP / API key; fail open or closed per policy
3. **Request context** — request id, auth subject, workspace id
4. **Exception handlers** — map domain errors to [API_SPEC.md](API_SPEC.md) error envelope

Optional: **Metrics** middleware for request duration histograms.

---

## 3. API surface (`/api/v1`) — route modules

| Router group | Prefix | Responsibility |
|--------------|--------|----------------|
| `health` | `/health`, `/ready` | Liveness/readiness |
| `documents` | `/documents` | Ingest registration, list, delete |
| `indexes` | `/indexes` | Index create, status, rebuild |
| `query` | `/query` | RAG query |
| `experiments` | `/experiments` | CRUD + `run` |
| `evaluations` | `/evaluations` | Eval jobs + reports |
| `metrics` | `/metrics` | Prometheus (optional, auth) |
| `auth` | `/auth` | If JWT/password auth is productized |

Detailed methods: [API_SPEC.md](API_SPEC.md).

---

## 4. Service layer (domain packages)

| Package | Key services |
|---------|----------------|
| `ingestion` | `DocumentLoader`, `IngestionService`, dedup, OCR orchestration |
| `chunking` | `ChunkingService` with strategy registry |
| `embedding` | `EmbeddingService`, provider clients |
| `vector_store` | `IndexService`, query adapters |
| `retrieval` | `RetrievalService`, hybrid fusion, rerankers |
| `generation` | `GenerationService`, prompt registry, token budget |
| `evaluation` | `EvalDatasetService`, `EvalRunner`, metric aggregators |
| `orchestration` | `AutoRAGOrchestrator`, optimization policies |
| `experiments` | `ExperimentRegistry`, tracker bridges (MLflow/W&B) |

Rules: routers call services; services call repositories and integration clients — not the reverse.

---

## 5. Persistence layer

- **SQLAlchemy models** under `models/` matching [DB_SCHEMA.md](DB_SCHEMA.md).
- **Repositories** per aggregate (`DocumentRepository`, `ExperimentRepository`, …).
- **Vector store client** per provider under `vector_store/providers/`.

---

## 6. Background workers

| Queue / task family | Typical tasks |
|---------------------|---------------|
| `ingest` | Parse documents, persist chunks, enqueue embed |
| `embed` | Batch embed chunks, upsert vectors |
| `eval` | Run batched eval, write `metric_snapshots`, artifacts |
| `index` | Full rebuild, namespace rotation |

Worker processes share the same settings and DB credentials as API; scale independently.

---

## 7. Configuration and secrets

- All secrets via environment or secret manager injection.
- **Experiment config** YAML/JSON loaded into `experiments.config` JSONB and hashed for reproducibility.

---

## 8. Testing hooks

- Service-level tests with mocked LLM, embeddings, and vector clients ([.cursor/rules/80-testing-quality.mdc](../.cursor/rules/80-testing-quality.mdc)).
- API tests for auth, pagination, and error envelopes.

---

## 9. Related documents

- [HDL.md](HDL.md)
- [ARCHITECTURE.md](ARCHITECTURE.md)
- [API_SPEC.md](API_SPEC.md)
- [DB_SCHEMA.md](DB_SCHEMA.md)
- [DEPLOYMENT.md](DEPLOYMENT.md)
- [CLAUDE.md](../CLAUDE.md)
