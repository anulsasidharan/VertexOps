# VertexOps — Product Requirements

> **Specification:** This document describes the **VertexOps** product as defined in [CLAUDE.md](../CLAUDE.md). It is the authoritative requirements baseline for ingestion through deployment. The repository implementation may lag this specification until features are built.

---

## 1. Product summary

**VertexOps** is an end-to-end **LLMOps platform** for model deployment, monitoring, fine-tuning, Retrieval-Augmented Generation (RAG), vector search, CI/CD automation, and secure production operations.

**Primary personas**

| Persona | Needs |
|--------|--------|
| **ML / AI engineer** | Fast iteration on chunking, embeddings, retrieval, and eval without one-off scripts everywhere |
| **AI platform team** | Repeatable experiments, metrics, rollback, and deployment paths |
| **Researcher / tech lead** | Comparable runs, config-as-code, and traceability from corpus to metrics |

**Out of scope for MVP** (see [CLAUDE.md](../CLAUDE.md) Advanced Features): graph RAG, full multi-tenant SaaS billing, native mobile apps, and other items explicitly marked post-MVP there — unless promoted into a future PRD revision.

---

## 2. Technology stack (target)

| Layer | Target implementation |
|-------|------------------------|
| **Runtime** | Python 3.11+ |
| **API** | FastAPI, async I/O |
| **RAG frameworks** | LangChain and/or LlamaIndex |
| **LLMs** | OpenAI, Anthropic, Google AI, Azure OpenAI; optional local (Ollama / LM Studio) |
| **Embeddings** | sentence-transformers, OpenAI, Cohere; pluggable |
| **Vector DBs** | Chroma, Pinecone, Qdrant, Weaviate, FAISS, Milvus (adapters) |
| **Lexical search** | BM25 (e.g. rank-bm25) for hybrid retrieval |
| **Evaluation** | RAGAS, deepeval-style metrics; custom reports |
| **Experiment tracking** | MLflow, Weights & Biases |
| **Relational metadata** | PostgreSQL, SQLAlchemy 2.0, Alembic |
| **Cache / broker** | Redis optional (rate limits, cache, Celery broker) |
| **Jobs** | Celery or equivalent for long-running ingest, embed, index, eval |
| **Dashboard (post-MVP UI)** | React 18, TypeScript, Vite, Tailwind, Recharts |
| **Observability** | Prometheus, Grafana, OpenTelemetry; structured logs |

---

## 3. Functional requirements (mapped to CLAUDE.md)

### 3.1 Document ingestion and processing

- Multi-format support: PDF, DOCX, TXT, Markdown, HTML, CSV.
- Optional OCR for scanned documents.
- Metadata extraction (title, author, date, source).
- Language detection; text cleaning and normalization.
- Document deduplication (hash / similarity).

### 3.2 Chunking

- Fixed-size, recursive, semantic, markdown-aware, and code-aware strategies.
- Configurable size, overlap, and strategy selection (manual or orchestrator-driven).
- Chunk lineage linked to source documents.

### 3.3 Embedding and vectorization

- Pluggable embedding providers and models; batching and rate limiting.
- Optional embedding cache; dimension and cost awareness.

### 3.4 Vector database integration

- Adapters for multiple vector DBs; index create/update/delete; metadata filtering.
- Index versioning or namespaces for experiments and environments.

### 3.5 Retrieval

- Vector similarity search; hybrid vector + BM25; MMR; optional multi-query and HyDE.
- Optional reranking (cross-encoder, Cohere rerank API, etc.).
- Parent–child or small-chunk retrieve patterns when configured.
- Configurable top_k and filters.

### 3.6 LLM integration and generation

- Multi-provider LLM adapters; prompt template library; context window / token budgeting.
- Streaming where supported; fallback chains optional.

### 3.7 Automated evaluation

- Synthetic test set generation from corpus; ground-truth answers.
- Metrics: relevance, context precision/recall, faithfulness, correctness, latency, cost per query.
- Regression comparison vs baselines; exportable reports (JSON / HTML artifacts).

### 3.8 Self-improvement and optimization

- Failure analysis and categorization.
- Grid / Bayesian search over key hyperparameters.
- Strategy switching with explicit rules and rollback to best-known config.
- Convergence detection and iteration caps.

### 3.9 Experiment management and logging

- Config-as-code (YAML/JSON); experiment and run IDs; artifact storage.
- MLflow / W&B integration for params, metrics, artifacts.

### 3.10 Deployment and production packaging

- FastAPI service with documented REST surface (see [API_SPEC.md](API_SPEC.md)).
- Docker / Compose; Kubernetes manifests; Terraform (or Pulumi) examples for cloud neutrality.
- Health and readiness endpoints; optional Prometheus `/metrics`.
- Rate limiting and authentication for production.

---

## 4. Interfaces

- **REST API:** primary surface for ingest, query, experiments, and eval (see [API_SPEC.md](API_SPEC.md)).
- **Optional CLI:** `autorag`-style commands aligned with the same services ([CLAUDE.md](../CLAUDE.md) Quick Start).
- **Optional web dashboard:** upload, playground, experiment charts ([CLAUDE.md](../CLAUDE.md) §19).

---

## 5. MVP roadmap (from CLAUDE.md)

| Phase | Theme | Highlights |
|-------|--------|------------|
| **Phase 1** | Foundation | Ingest (PDF/DOCX/TXT), fixed chunking, single embedding path, Chroma/Pinecone-style index, basic vector retrieval, single LLM path, `/query` API |
| **Phase 2** | Evaluation and optimization | Synthetic eval set, RAGAS-style metrics, hyperparameter search, multiple chunking strategies, multiple embedders, hybrid search, MLflow |
| **Phase 3** | Production readiness | Reranking, multi-LLM, Docker/K8s, Terraform, Prometheus/Grafana, CI/CD, basic web playground |
| **Phase 4** | Advanced | Multi-query, HyDE, parent–child, visual pipeline builder, A/B testing, HITL eval UI, cost analytics |

---

## 6. Success criteria (product / technical targets from CLAUDE.md)

- Sub **2s p95** query latency under reference load (tunable by model and hardware).
- High **faithfulness** and **answer relevance** on internal eval sets (concrete thresholds set per deployment).
- **Cost per query** tracked and optimizable.
- **One-command** or documented minimal path from corpus to deployed API for the happy path.

---

## 7. Security and compliance (requirements)

- No secrets in code or images; use secret managers in production.
- Treat uploads and user queries as untrusted; **prompt injection** mitigations for RAG.
- PII handling for indexed documents; audit logs for sensitive actions (see [.cursor/rules/70-security.mdc](../.cursor/rules/70-security.mdc)).
- Rate limits on ingest, embed, eval, and query endpoints.

---

## 8. Related engineering docs

- [ARCHITECTURE.md](ARCHITECTURE.md) — logical components and data flow
- [API_SPEC.md](API_SPEC.md) — HTTP API specification
- [DB_SCHEMA.md](DB_SCHEMA.md) — metadata and lineage schema
- [DEPLOYMENT.md](DEPLOYMENT.md) — environments and operations
- [HDL.md](HDL.md) — high-level design
- [LDL.md](LDL.md) — low-level module and route map

Canonical feature depth and examples: **[CLAUDE.md](../CLAUDE.md)**.
