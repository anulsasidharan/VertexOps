# VertexOps — Interview Questions and Answers

> **Purpose:** A structured Q&A bank for technical interviews about the **VertexOps** project. Answers align with [CLAUDE.md](../CLAUDE.md), [PRD.md](PRD.md), [ARCHITECTURE.md](ARCHITECTURE.md), [API_SPEC.md](API_SPEC.md), [DB_SCHEMA.md](DB_SCHEMA.md), and [DEPLOYMENT.md](DEPLOYMENT.md). The live codebase may differ until fully implemented; treat the docs as the product baseline.

---

## Table of contents

1. [Product and domain](#1-product-and-domain)
2. [System architecture](#2-system-architecture)
3. [RAG pipeline (ingestion → query)](#3-rag-pipeline-ingestion--query)
4. [Retrieval and generation](#4-retrieval-and-generation)
5. [Evaluation and optimization](#5-evaluation-and-optimization)
6. [APIs and integration](#6-apis-and-integration)
7. [Data model and persistence](#7-data-model-and-persistence)
8. [Security, compliance, and reliability](#8-security-compliance-and-reliability)
9. [Cloud, deployment, and operations](#9-cloud-deployment-and-operations)
10. [Testing and quality](#10-testing-and-quality)
11. [Trade-offs and system design](#11-trade-offs-and-system-design)
12. [Behavioral and ownership](#12-behavioral-and-ownership)

---

## 1. Product and domain

### Q1.1 — What is VertexOps?

**A:** VertexOps is an end-to-end **LLMOps** platform for deploying, monitoring, and operating generative AI applications. It covers model lifecycle concerns, **RAG** (retrieval-augmented generation), **vector search**, **evaluation**, **experiment tracking**, **optimization loops**, and **production-oriented deployment** (containers, CI/CD, observability), with a **FastAPI** service as the primary integration surface.

### Q1.2 — Who are the main users?

**A:** Typical personas include **ML/AI engineers** (iterate on chunking, embeddings, retrieval), **AI platform teams** (repeatable experiments, rollback, deployment paths), and **research or tech leads** (comparable runs, config-as-code, traceability from corpus to metrics).

### Q1.3 — What is explicitly out of scope for the MVP?

**A:** Per product docs, examples include **graph RAG**, full **multi-tenant SaaS billing**, **native mobile apps**, and other items marked post-MVP unless the PRD is revised. [CLAUDE.md](../CLAUDE.md) also lists initial non-GCP cloud as out of scope for the *baseline* product narrative, while deployment docs may mention optional parity paths—candidates should distinguish **product baseline** vs **optional deployment docs**.

### Q1.4 — What does “success” look like for the product?

**A:** Targets include **sub ~2s p95 query latency** under reference load (tunable), strong **faithfulness** and **answer relevance** on internal eval sets, **cost per query** visibility and optimization, and a **minimal documented path** from corpus to a deployed query API for the happy path.

---

## 2. System architecture

### Q2.1 — Describe the high-level architecture in one minute.

**A:** Clients (optional **web dashboard**, **CLI**, external **API consumers**) call a **FastAPI** API. Core services implement **ingestion**, **chunking**, **embedding**, **vector store adapters**, **retrieval**, **generation**, **evaluation**, and **experiment** orchestration. An **orchestrator** can drive strategy selection and optimization. **PostgreSQL** stores metadata and lineage; a **vector database** stores embeddings; **object storage** holds raw documents and large artifacts; **LLM providers** answer queries; **MLflow** or **Weights & Biases** tracks experiment params and metrics.

### Q2.2 — Why separate metadata (PostgreSQL) from vectors (vector DB)?

**A:** Relational stores excel at **ACID metadata**, joins, filtering, and audit-friendly records (documents, chunks, experiments, runs). Vector stores optimize **similarity search** at scale. Keeping embeddings out of Postgres (unless explicitly designed otherwise) avoids bloating the OLTP database and lets teams swap vector backends via **adapters**.

### Q2.3 — What is the orchestrator responsible for?

**A:** It decides **strategies** (chunking, embedding, retrieval), runs **experiments**, and drives the **optimization loop** (search, failure analysis, rollback to best-known configs). It may use stateful workflow tools (e.g. LangGraph-style patterns) where appropriate.

### Q2.4 — How does the platform handle long-running work?

**A:** Lightweight paths stay on the **synchronous API** (health, status, warm queries). Heavy work—bulk ingest, re-embed, index rebuild, large eval sweeps—runs as **background jobs** (e.g. **Celery** queues like `ingest`, `embed`, `eval`). **Idempotency** uses hashes (`content_hash`, `config_hash`) and index **namespace/version** for safe retries.

### Q2.5 — What cross-cutting concerns span all layers?

**A:** **Authentication** (JWT/API keys), **authorization** (RBAC/scopes when multi-user), **rate limiting** (especially ingest, rebuild, eval, query), **structured logging**, **metrics/tracing** (Prometheus/OpenTelemetry), and **consistent error envelopes** on the API.

---

## 3. RAG pipeline (ingestion → query)

### Q3.1 — Walk through the offline indexing path.

**A:** **Documents** are loaded (PDF, DOCX, TXT, Markdown, HTML, CSV; optional OCR). Text is **cleaned**, **metadata** extracted, **language** detected, and **deduplication** applied (hash/similarity). **Chunking** produces segments with lineage back to the source document. **Embeddings** are computed in batches with rate limits and optional caching. Vectors are **indexed** in the configured vector backend with metadata for filtering.

### Q3.2 — What chunking strategies should the platform support?

**A:** The PRD calls for **fixed-size**, **recursive**, **semantic**, **markdown-aware**, and **code-aware** strategies, with configurable size/overlap and manual or orchestrator-driven selection. Chunks should retain **lineage** to source documents.

### Q3.3 — How would you add a new document format safely?

**A:** Validate **MIME/type**, enforce **size limits**, run parsing in a **sandboxed** path where possible, normalize to text, strip risky content, and reject unsupported executables. Persist **ingest_status** and structured errors for operators. Never trust file extensions alone.

### Q3.4 — What is “chunk lineage” and why does it matter?

**A:** Lineage ties each chunk to its **source document** (and position/section path). It powers **explainable answers** (citations), **re-indexing** when upstream docs change, **debugging** retrieval failures, and **compliance** (deletion/export scoped to a document).

---

## 4. Retrieval and generation

### Q4.1 — What retrieval capabilities are in scope?

**A:** **Vector similarity**, **hybrid** vector + **BM25**, **MMR** for diversity, optional **multi-query** and **HyDE** (post-MVP in roadmap), optional **reranking** (cross-encoder or vendor rerank APIs), and **parent–child** or small-chunk retrieve patterns when configured. **top_k** and metadata **filters** should be configurable.

### Q4.2 — Why use hybrid retrieval (dense + sparse)?

**A:** Dense retrieval captures **semantic** similarity but can miss **lexical** matches (SKUs, rare tokens, exact policy clauses). BM25-style sparse retrieval complements embeddings. Fusion strategies (e.g. weighted or RRF) combine both signals.

### Q4.3 — How do you budget context for the LLM?

**A:** Track **token counts** for chunks, apply a **max context** policy, prioritize by **relevance scores** and optional **reranker** order, deduplicate overlapping chunks, and reserve budget for **system instructions**, **tool outputs**, and the **user question**. Fail gracefully with partial context rather than silent truncation bugs.

### Q4.4 — How do you mitigate prompt injection in RAG?

**A:** Treat **user queries** and **document text** as untrusted. Use **delimiter** patterns, **instruction hierarchy**, **output validation** before persistence, **tool allowlists**, **role/scoped** policies, and avoid echoing secrets. Log safely without storing raw sensitive document content.

---

## 5. Evaluation and optimization

### Q5.1 — What does automated evaluation include?

**A:** Synthetic or curated **test sets**, metrics such as **relevance**, **context precision/recall**, **faithfulness**, **correctness**, **latency**, and **cost per query**, plus **regression** comparisons vs baselines and **exportable** reports (JSON/HTML artifacts).

### Q5.2 — Name frameworks or patterns mentioned for metrics.

**A:** Docs reference **RAGAS** and **deepeval-style** metrics as examples; custom aggregations and reports are also expected for enterprise needs.

### Q5.3 — How does “self-improvement” work without unsafe autonomy?

**A:** Use **explicit rules** for strategy switches, **bounded search** (grid/Bayesian) over key hyperparameters, **failure categorization**, **convergence** checks and **iteration caps**, and **rollback** to the best-known configuration. Critical production changes should be **gated** (human approval) where required.

### Q5.4 — What is experiment tracking for?

**A:** To tie **config-as-code** snapshots to **runs**, store **parameters** and **metrics**, and reference **artifacts** in MLflow/W&B so teams can compare experiments reproducibly.

---

## 6. APIs and integration

### Q6.1 — What is the recommended API base path and documentation?

**A:** **`/api/v1`** as the versioned base. **OpenAPI** at `/openapi.json` when enabled; interactive **`/docs`** may be disabled in strict production.

### Q6.2 — How are errors represented?

**A:** A consistent **error envelope** with `code`, `message`, and optional `details` (e.g. `VALIDATION_ERROR`, `RATE_LIMIT_EXCEEDED`, `NOT_FOUND`). Avoid leaking **internal stack traces** to clients.

### Q6.3 — List core authenticated endpoint groups.

**A:** Examples from the spec: **models** (`/models/deploy`, fine-tune, status), **RAG** (`/rag/query`), **vector** (`/vector/search`), **documents** (ingest/list/detail/delete), **indexes** (create/list/rebuild), **`/query`**, **experiments** and **runs**, **evaluations** and **reports**, **monitoring/metrics**, optional **`/metrics`** for Prometheus.

### Q6.4 — How does auth work?

**A:** **Bearer JWT** and/or **API key** header (e.g. `X-API-Key`). Public **register** may be gated by configuration (e.g. `ALLOW_PUBLIC_SIGNUP`). API keys are created and revoked via authenticated endpoints.

### Q6.5 — How should uploads be designed at scale?

**A:** Prefer **signed URL** flows: register intent, upload to **object storage**, then **complete** ingestion—reduces load on the API and supports large files.

---

## 7. Data model and persistence

### Q7.1 — What entities live in PostgreSQL?

**A:** Prescriptive schema includes **workspaces** (optional multi-tenant boundary), **users**, **documents**, **chunks**, **indexes**, **experiments**, **runs**, **eval_cases**, **metric_snapshots**, **deployments**—metadata and lineage, not the embedding vectors themselves (by default).

### Q7.2 — What fields support deduplication and reproducibility?

**A:** **`content_hash`** on documents, **`config_hash`** on indexes/experiments, **`vector_id`** linking chunks to vector DB records, and timestamps for auditing.

### Q7.3 — How are indexes versioned conceptually?

**A:** Indexes carry **namespace** (provider-specific), **config** JSON snapshots, **config_hash**, and **status** (`building`, `ready`, `failed`) so teams can run **A/B** or **shadow** configurations without destroying production namespaces.

---

## 8. Security, compliance, and reliability

### Q8.1 — Where must secrets live?

**A:** Never in code or images. Use **environment variables** locally and **secret managers** (e.g. GCP Secret Manager) in production, with **rotation** and least-privilege IAM.

### Q8.2 — What endpoints deserve stricter rate limits?

**A:** **Ingest**, **bulk embed**, **index rebuild**, **eval runs**, and high-volume **query**—these are expensive or abuse-prone.

### Q8.3 — What compliance-oriented requirements appear in the PRD?

**A:** **PII** handling/masking where required, **audit logs** for sensitive actions (document access, experiment/config changes, API key usage, deployment/rollback), and **GDPR-style** capabilities (export/deletion/retention) where applicable.

### Q8.4 — How should downstream failures be handled?

**A:** Patterns include **retries with backoff** for transient vector search issues, **circuit breakers**, **clear client errors**, **structured logs** with correlation IDs, and **webhooks/alerts** for pipeline failures where implemented.

---

## 9. Cloud, deployment, and operations

### Q9.1 — What is the primary production topology in the deployment guide?

**A:** **GCP Cloud Run** for `vertexops-api` and optional `vertexops-worker`, with **Cloud SQL (PostgreSQL)**, **Memorystore (Redis)**, **GCS** for objects, and a vector backend such as **Pinecone** or **Vertex Matching Engine**, plus **Cloud Logging/Trace** and optional **Prometheus `/metrics`**.

### Q9.2 — How do you run locally per DEPLOYMENT.md?

**A:** Use **`uv sync`**, configure **`.env` from `.env.example`**, bring up **`docker compose`** for Postgres/Redis (and worker profile if needed), run **`alembic upgrade head`**, optionally **`scripts.bootstrap_dev_user`** for a dev admin.

### Q9.3 — What Dockerfile targets exist?

**A:** **`runtime-base`**, **`api`** (Uvicorn), and **`worker`** (Celery). Images should run as **non-root**, without build tools in runtime, and use **health checks** (`/api/v1/health` for API; Celery inspect for workers).

### Q9.4 — Name important environment variables.

**A:** Examples: **`DATABASE_URL`**, **`REDIS_URL`**, Celery broker/result URLs, **`JWT_SECRET_KEY`**, **`API_KEY_PEPPER`**, **`GCP_PROJECT_ID`**, **`VERTEX_AI_LOCATION`**, optional **`OPENAI_API_KEY`**, **`PINECONE_API_KEY`**, **`GCS_BUCKET_NAME`**, **`APP_ENV`**.

### Q9.5 — How does CI/CD fit the product story?

**A:** Automated **build, test, and deploy** (e.g. **Cloud Build**, **GitHub Actions**) ensures repeatable releases, canaries/rollbacks where adopted, and aligns with LLMOps goals of safe model and config promotion.

---

## 10. Testing and quality

### Q10.1 — What should unit tests emphasize?

**A:** Deterministic logic: **chunking**, **retrieval fusion**, **metric aggregation**, and **orchestrator rules**—with **mocks** for LLMs, embeddings, vector DBs, object storage, and Postgres in unit tests.

### Q10.2 — What belongs in integration tests?

**A:** **API routes**, **repositories**, **pipelines** crossing process boundaries, **auth/RBAC** flows, and **job/worker** handoffs—often with test containers or ephemeral services.

### Q10.3 — What should you never depend on in default CI?

**A:** Live calls to paid **LLM**, **embedding**, or **vector** endpoints; tests should be **isolated** and **hermetic** unless explicitly marked as external/e2e smoke tests.

---

## 11. Trade-offs and system design

### Q11.1 — Pinecone vs self-hosted Qdrant/Weaviate—how would you choose?

**A:** Consider **ops burden**, **latency SLOs**, **metadata filtering** needs, **compliance/data residency**, **cost model** (per pod vs hosted units), **multi-region**, and **team skill**. VertexOps uses **adapters** so the product can support multiple backends; default examples may be GCP-first.

### Q11.2 — When would you synchronous vs async a query?

**A:** If retrieval+generation fits **latency SLO** and indexes are **warm**, synchronous is simpler. If the request chains many tools or large retrieval fan-out, consider **streaming** responses and/or **async jobs** with polling/webhooks for heavy analytical queries.

### Q11.3 — How would you design multi-tenancy later?

**A:** Introduce **`workspace_id`** on all resources, **row-level** isolation in Postgres, **separate index namespaces** per tenant, **strict authZ** checks in services (not only routes), **per-tenant rate limits** and quotas, and **audit** trails per tenant.

### Q11.4 — How do you prevent cost explosions?

**A:** **Rate limits**, **quotas**, **batch sizing**, **caching** embeddings, **smaller models** for retrieval steps, **eval sampling**, **budget alerts**, and **cost-per-query** metrics in dashboards.

---

## 12. Behavioral and ownership

### Q12.1 — Tell me about a time you debugged a bad RAG answer.

**A:** *(Framework)* Reproduce with **logged query id**, inspect **retrieved chunks** and scores, verify **chunking** boundaries, check **filters** and **index version**, test **embedding model** drift, review **prompt template** changes, and run **eval regression** before shipping a fix.

### Q12.2 — How do you prioritize MVP scope?

**A:** Ship **ingest → chunk → embed → index → `/query`** first, then **eval + experiments**, then **production hardening** (auth, rate limits, observability, HA jobs), then **advanced retrieval** and UI—aligned with phased roadmap in the PRD.

### Q12.3 — How do you communicate breaking API changes?

**A:** **Version** routes (`/api/v1`), document deprecations in **API_SPEC**, maintain **migration guides**, use **OpenAPI diff** in CI, and offer **dual-run** periods for integrators where feasible.

---

## Quick flashcard section (short answers)

| Topic | Short answer |
|--------|----------------|
| Core stack | Python 3.11+, FastAPI, PostgreSQL, vector DB adapters, Redis optional, Celery jobs |
| Primary clients | REST API; optional CLI and React dashboard |
| Vector storage | Chroma, Pinecone, Qdrant, Weaviate, FAISS, Milvus, Vertex Matching Engine (via adapters) |
| Retrieval extras | Hybrid BM25, MMR, rerankers, filters |
| Eval tools | RAGAS-style metrics, reports, experiment runs |
| GCP services | Vertex AI, Matching Engine, Cloud Run, Cloud SQL, GCS, Cloud Logging/Trace |
| Security pillars | Secrets management, RBAC/API keys, rate limits, prompt injection defenses, audit logs |
| Idempotency | `content_hash`, `config_hash`, index namespace/version |

---

## Related documents

- [PRD.md](PRD.md) — requirements and roadmap  
- [ARCHITECTURE.md](ARCHITECTURE.md) — components and data flow  
- [API_SPEC.md](API_SPEC.md) — HTTP contracts  
- [DB_SCHEMA.md](DB_SCHEMA.md) — relational metadata  
- [DEPLOYMENT.md](DEPLOYMENT.md) — environments and operations  
- [CLAUDE.md](../CLAUDE.md) — canonical platform description  

---

**Document version:** 1.0  
**Last updated:** April 2026  
