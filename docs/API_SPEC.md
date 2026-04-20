# VertexOps — HTTP API Specification

> **Specification:** REST surface for **VertexOps** aligned with [CLAUDE.md](../CLAUDE.md) and [PRD.md](PRD.md). Paths and payloads are prescriptive; implementation may use slightly different names until the codebase matches this document.

**Base path:** `/api/v1` (recommended)
**OpenAPI:** Served at `/openapi.json` when enabled; `/docs` optional outside strict production lockdown.

---

## 1. Conventions

### 1.1 Success envelope (optional)

Implementations may wrap JSON success bodies consistently, for example:

```json
{ "data": { ... } }
```

If wrapping is used, skip double-wrapping when the handler already returns `data` or `error`. **Health** and **metrics** endpoints are typically unwrapped.

### 1.2 Error envelope

```json
{
  "error": {
    "code": "NOT_FOUND",
    "message": "Document not found",
    "details": {}
  }
}
```

**Suggested codes:** `UNAUTHORIZED`, `FORBIDDEN`, `NOT_FOUND`, `CONFLICT`, `VALIDATION_ERROR`, `RATE_LIMIT_EXCEEDED`, `INTERNAL_ERROR`.

### 1.3 Authentication

- **Bearer JWT** and/or **API key** header (exact header name product-defined, e.g. `X-API-Key`).
- Scoped access for workspace-scoped resources when multi-tenant features exist.

### 1.4 Pagination

- List endpoints use `page` + `page_size` or `cursor` + `limit` with documented max page size.

### 1.5 Rate limiting

- Stricter tiers for **ingest**, **index rebuild**, **eval run**, and high-volume **query**; return **429** with retry hints when exceeded.

---

## 2. Health and readiness

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/health` | No | Liveness — process up |
| GET | `/ready` | No | Readiness — DB, vector index, critical deps reachable |

---

## 3. Authentication

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/auth/register` | No | Create user (email + password); returns JWT **201** when `ALLOW_PUBLIC_SIGNUP` is enabled |
| POST | `/auth/token` | No | Issue JWT access token (email + password) |
| POST | `/auth/api-keys` | Yes | Create API key for the authenticated user |
| GET | `/auth/api-keys` | Yes | List API keys for the authenticated user |
| DELETE | `/auth/api-keys/{key_id}` | Yes | Revoke an API key |

**Token request:**

```json
{ "email": "user@example.com", "password": "secret" }
```

**Token response:**

```json
{ "access_token": "<jwt>", "token_type": "bearer" }
```

---

## 4. Core model and RAG endpoints (CLAUDE baseline)

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/models/deploy` | Yes | Deploy model/provider configuration |
| POST | `/models/{model_id}/finetune` | Yes | Trigger fine-tuning workflow |
| POST | `/rag/query` | Yes | Execute retrieval-augmented generation query |
| POST | `/vector/search` | Yes | Run vector similarity search |
| GET | `/models/{model_id}/status` | Yes | Get model deployment/training status |
| GET | `/monitoring/metrics` | Yes | Fetch model or service metrics |

---

## 5. Documents and ingestion

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/documents` | Yes | Register upload or URL ingest job |
| GET | `/documents` | Yes | List documents with filters |
| GET | `/documents/{document_id}` | Yes | Metadata and ingest status |
| DELETE | `/documents/{document_id}` | Yes | Remove document and associated chunks/index entries (async acceptable) |

**Upload pattern (example):** `POST /documents/upload-url` → returns signed URL + `document_id`; client uploads to object storage; `POST /documents/{id}/complete` finalizes ingest.

---

## 6. Indexing and pipelines

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/indexes` | Yes | Create or update index from corpus with config body (chunking, embedding, vector backend) |
| GET | `/indexes` | Yes | List indexes / namespaces |
| GET | `/indexes/{index_id}` | Yes | Status, stats |
| POST | `/indexes/{index_id}/rebuild` | Yes | Re-embed / re-chunk per new config (async job) |

---

## 7. Query (RAG)

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/query` | Yes | Run retrieval + generation |

**Example request:**

```json
{
  "question": "What is the return policy?",
  "index_id": "idx_prod_docs",
  "filters": { "doc_type": "user_guide" },
  "top_k": 5,
  "stream": false
}
```

**Example response:**

```json
{
  "answer": "To reset your password...",
  "sources": [
    { "chunk_id": "doc_123_chunk_5", "score": 0.92, "document_id": "doc_123" }
  ],
  "latency_ms": 1250,
  "experiment_id": null
}
```

---

## 8. Experiments

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/experiments` | Yes | Create experiment from config payload |
| GET | `/experiments` | Yes | List experiments |
| GET | `/experiments/{experiment_id}` | Yes | Detail, last run summary |
| POST | `/experiments/{experiment_id}/run` | Yes | Start run (ingest → index → optional eval) |
| GET | `/experiments/{experiment_id}/runs` | Yes | List runs |

---

## 9. Evaluation

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/evaluations` | Yes | Start eval job for an index + dataset |
| GET | `/evaluations/{eval_id}` | Yes | Status and summary metrics |
| GET | `/evaluations/{eval_id}/report` | Yes | Download JSON/HTML artifact URL or inline payload |

---

## 10. Metrics and observability (optional)

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/metrics` | Internal or auth | Prometheus text format |

---

## 11. Webhooks (optional, post-MVP patterns)

- Outbound signed webhooks for **eval complete**, **index build complete**, or **deployment status** — document payload schema alongside implementation.

---

## 12. Related documents

- [PRD.md](PRD.md) — requirements
- [ARCHITECTURE.md](ARCHITECTURE.md) — components
- [DB_SCHEMA.md](DB_SCHEMA.md) — persisted entities
- [DEPLOYMENT.md](DEPLOYMENT.md) — environments
