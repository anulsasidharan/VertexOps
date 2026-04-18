# VertexOps Development Roadmap

This file is the implementation roadmap for `development`-bound feature branches.
Each task is intentionally scoped to a mergeable `feature/*` branch that should
fit into roughly 2-8 hours of focused work, stay independently testable, and
minimize merge conflicts.

The roadmap is aligned to `CLAUDE.md`, `docs/PRD.md`, `docs/ARCHITECTURE.md`,
`docs/API_SPEC.md`, `docs/DB_SCHEMA.md`, `docs/DEPLOYMENT.md`, `docs/HDL.md`,
and `docs/LDL.md`.

## Planning Rules

- Branch flow: `main <- development <- feature/*`
- Prefer GCP-first implementation for VertexOps defaults.
- Treat AWS-specific deployment as optional parity work, not the product baseline.
- Post-MVP items are included only when they help future planning; core delivery
  should prioritize foundation, RAG, evaluation, and deployment first.
- `Parallelizable With` indicates safe concurrent work once listed dependencies are done.

## Table of Contents

- [Phase 1 - Foundation and Project Skeleton](#phase-1---foundation-and-project-skeleton)
- [Phase 2 - Data Model and Security Foundation](#phase-2---data-model-and-security-foundation)
- [Phase 3 - Ingestion and Indexing Pipeline](#phase-3---ingestion-and-indexing-pipeline)
- [Phase 4 - Retrieval and Generation](#phase-4---retrieval-and-generation)
- [Phase 5 - Experiments, Evaluation, and Optimization](#phase-5---experiments-evaluation-and-optimization)
- [Phase 6 - Frontend and Product Integrations](#phase-6---frontend-and-product-integrations)
- [Phase 7 - Observability, Deployment, and Delivery](#phase-7---observability-deployment-and-delivery)
- [Phase 8 - Final Quality and Documentation](#phase-8---final-quality-and-documentation)

## Phase Overview

| Phase | Goal | Primary Blocking Output | Parallel Lanes | Status |
|------|------|--------------------------|----------------|--------|
| 1 | Bootstrap repo structure and runtime | App skeleton, config, local infra | Tasks 2-4 after Task 1 | ✅ Complete (Tasks 1-4) |
| 2 | Establish DB, auth, and API base | Schema, auth, health, rate limits | Tasks 6-9 after Task 5 | ✅ Complete (Tasks 5-10) |
| 3 | Build ingest to index pipeline | Upload, chunk, embed, vector indexing, workers | Tasks 12-17 after Task 11 | ✅ Complete (Tasks 11-19 ✅) |
| 4 | Deliver RAG query capabilities | Retrieval, generation, citations, realtime | Tasks 21-24 after Task 20 | ✅ Complete (Tasks 20-25 ✅) |
| 5 | Add experiments and optimization loop | Experiment runs, eval reports, orchestrator | Tasks 27-30 after Task 26 | Complete (Tasks 26-30) |
| 6 | Add UI and external product hooks | Dashboard, notifications, billing hooks | Tasks 32-35 after Task 31 | Not Started |
| 7 | Make platform deployable and automatable | Metrics, containers, CI/CD, cloud envs | Tasks 37-40 after Task 36 | Not Started |
| 8 | Finish quality bar and release docs | E2E, hardening, roadmap closeout | Tasks 41-42 after Task 40 | Not Started |

---

## Phase 1 - Foundation and Project Skeleton

## Task #1: Repository Application Skeleton ✅
- **Branch:** `feature/app-skeleton`
- **Dependencies:** None
- **Parallelizable With:** None
- **Description:** Create the initial backend and frontend folder conventions from `docs/ARCHITECTURE.md` and `docs/LDL.md`, including FastAPI entrypoint, shared settings package, placeholder domain modules, test layout, and optional `frontend/` shell.
- **Acceptance Criteria:**
- Backend root exists with `api`, `core`, domain packages, `models`, `repositories`, and `workers` directories.
- FastAPI app factory or `main.py` boots without domain features implemented.
- Test directory and package init files exist for unit and integration suites.
- Frontend folder structure is reserved without introducing business logic.
- **Files/Modules Affected:** `backend/`, `frontend/`, `tests/`, `pyproject.toml`, `requirements*.txt`
- **Estimated Complexity:** Medium

## Task #2: Environment Configuration and Settings Loader ✅
- **Branch:** `feature/settings-and-env`
- **Dependencies:** 1
- **Parallelizable With:** 3, 4
- **Description:** Implement typed environment configuration with `pydantic-settings`, environment grouping, local `.env.example`, and per-service config objects for app, database, Redis, auth, vector DB, LLMs, and observability.
- **Acceptance Criteria:**
- Central settings loader exposes validated config values.
- `.env.example` documents required variables by category.
- Sensitive settings are loaded only from environment, never hardcoded.
- App boot fails clearly on invalid required configuration.
- **Files/Modules Affected:** `backend/core/config.py`, `.env.example`, `backend/core/`
- **Estimated Complexity:** Low

## Task #3: Local Infrastructure Bootstrap ✅
- **Branch:** `feature/local-dev-infra`
- **Dependencies:** 1
- **Parallelizable With:** 2, 4
- **Description:** Create local development infrastructure definitions for API, PostgreSQL, Redis, and placeholder worker service using Docker Compose, following `docs/DEPLOYMENT.md`.
- **Acceptance Criteria:**
- `docker-compose.yml` starts API dependencies locally.
- Service names and ports align with deployment documentation.
- API can resolve local database and Redis connection URLs.
- Container-level environment separation is documented in comments or README updates.
- **Files/Modules Affected:** `docker-compose.yml`, `Dockerfile`, `.dockerignore`, `docs/DEPLOYMENT.md`
- **Estimated Complexity:** Medium

## Task #4: Shared Logging, Exceptions, and Request Context ✅
- **Branch:** `feature/core-logging-and-errors`
- **Dependencies:** 1
- **Parallelizable With:** 2, 3
- **Description:** Add structured logging, common exception classes, error-envelope helpers, request ID context, and base middleware hooks for production-safe API behavior.
- **Acceptance Criteria:**
- Structured log formatter is available to API and workers.
- Shared exception mapping supports `VALIDATION_ERROR`, `FORBIDDEN`, `NOT_FOUND`, and `INTERNAL_ERROR`.
- Request context exposes request ID and auth subject placeholders.
- Error responses follow `docs/API_SPEC.md`.
- **Files/Modules Affected:** `backend/core/logging.py`, `backend/core/exceptions.py`, `backend/api/`, `backend/core/middleware/`
- **Estimated Complexity:** Medium

✅ Milestone 1: Project Skeleton Complete

---

## Phase 2 - Data Model and Security Foundation

## Task #5: Database Engine, Session Management, and Alembic Setup ✅
- **Branch:** `feature/db-foundation`
- **Dependencies:** 2, 3, 4
- **Parallelizable With:** None
- **Description:** Configure SQLAlchemy 2.0, async DB session handling, Alembic migration environment, and repository base abstractions.
- **Acceptance Criteria:**
- App can create DB sessions from shared settings.
- Alembic is configured and can generate/apply migrations.
- Repository base pattern is established for future modules.
- Readiness checks can test DB connectivity.
- **Files/Modules Affected:** `alembic/`, `backend/core/db.py`, `backend/models/`, `backend/repositories/`
- **Estimated Complexity:** Medium

## Task #6: Workspace and User Schema Models
- **Branch:** `feature/schema-workspaces-users`
- **Dependencies:** 5
- **Parallelizable With:** 7, 8, 9
- **Description:** Implement `workspaces` and `users` SQLAlchemy models plus initial Alembic migration aligned with `docs/DB_SCHEMA.md`.
- **Acceptance Criteria:**
- SQLAlchemy models exist for `workspaces` and `users`.
- Migration creates required columns, timestamps, and uniqueness constraints.
- Repository layer can read and write users and workspaces.
- Basic seed or fixture support exists for tests.
- **Files/Modules Affected:** `backend/models/`, `backend/repositories/user_repository.py`, `alembic/versions/`, `tests/`
- **Estimated Complexity:** Medium

## Task #7: Document and Chunk Schema Models
- **Branch:** `feature/schema-documents-chunks`
- **Dependencies:** 5
- **Parallelizable With:** 6, 8, 9
- **Description:** Implement `documents` and `chunks` models, migration, indexes, and repository methods for lineage-aware ingestion state.
- **Acceptance Criteria:**
- `documents` and `chunks` tables match required fields and indexes.
- `ON DELETE CASCADE` behavior is configured for chunk cleanup.
- Repository methods support CRUD plus list/filter by ingest status.
- Tests cover model relationships and cascade behavior.
- **Files/Modules Affected:** `backend/models/`, `backend/repositories/document_repository.py`, `backend/repositories/chunk_repository.py`, `alembic/versions/`, `tests/`
- **Estimated Complexity:** Medium

## Task #8: Index, Experiment, Run, Metric, and Deployment Schema Models ✅
- **Branch:** `feature/schema-indexes-experiments`
- **Dependencies:** 5
- **Parallelizable With:** 6, 7, 9
- **Description:** Implement the remaining metadata schema for indexes, experiments, runs, eval cases, metric snapshots, and deployments.
- **Acceptance Criteria:**
- Models and migration cover all remaining prescribed metadata tables.
- Repositories expose basic create/get/list operations for each aggregate.
- JSONB config and metrics fields are typed or normalized consistently.
- Tests verify key foreign-key relationships and status fields.
- **Files/Modules Affected:** `backend/models/`, `backend/repositories/`, `alembic/versions/`, `tests/`
- **Estimated Complexity:** High

## Task #9: Authentication, API Keys, and RBAC Base ✅
- **Branch:** `feature/auth-rbac-base`
- **Dependencies:** 5, 6
- **Parallelizable With:** 7, 8
- **Description:** Add JWT and API key authentication primitives, password hashing if password auth is enabled, and role checks for protected routes.
- **Acceptance Criteria:**
- Shared auth dependency resolves either JWT or API key identity.
- Role checks support at least `admin`, `member`, and service/API contexts.
- Secrets and API key pepper are environment-based only.
- Auth unit tests cover unauthorized, forbidden, and success paths.
- **Files/Modules Affected:** `backend/api/dependencies/auth.py`, `backend/core/security.py`, `backend/models/user*.py`, `tests/`
- **Estimated Complexity:** High

## Task #10: Health, Readiness, and Rate Limiting Endpoints ✅
- **Branch:** `feature/health-ready-rate-limit`
- **Dependencies:** 4, 5, 9
- **Parallelizable With:** None
- **Description:** Implement `/health`, `/ready`, and shared rate-limiting middleware or dependency with Redis-backed support and safe fallback behavior.
- **Acceptance Criteria:**
- `/api/v1/health` returns liveness without auth.
- `/api/v1/ready` checks DB and critical configured dependencies.
- Rate limiting is enforced for protected routes with configurable policies.
- 429 responses match API error envelope expectations.
- **Files/Modules Affected:** `backend/api/v1/health.py`, `backend/core/middleware/`, `backend/core/rate_limit.py`, `tests/`
- **Estimated Complexity:** Medium

✅ Milestone 2: Backend Foundation Complete

---

## Phase 3 - Ingestion and Indexing Pipeline

## Task #11: Object Storage and File Handling Abstraction ✅
- **Branch:** `feature/object-storage-abstraction`
- **Dependencies:** 7, 10
- **Parallelizable With:** None
- **Description:** Implement an object storage abstraction for raw document storage and artifact persistence, with local/dev adapter plus GCP-ready interface shape.
- **Acceptance Criteria:**
- Storage service supports put/get/delete and signed-upload preparation interfaces.
- Local development adapter works without cloud credentials.
- Storage keys or URIs are persisted in document metadata flows.
- Tests cover successful upload references and delete cleanup.
- **Files/Modules Affected:** `backend/ingestion/storage/`, `backend/core/config.py`, `tests/`
- **Estimated Complexity:** Medium

## Task #12: Documents API for Register, List, Detail, and Delete ✅
- **Branch:** `feature/documents-api`
- **Dependencies:** 7, 9, 10, 11
- **Parallelizable With:** 13, 18
- **Description:** Build document endpoints for create/register, list, get, and delete flows, including validation and authorization checks.
- **Acceptance Criteria:**
- `POST /documents`, `GET /documents`, `GET /documents/{id}`, and `DELETE /documents/{id}` exist.
- Request and response schemas match documented API behavior.
- Workspace/user access checks are enforced consistently.
- API tests cover success, auth failure, and not-found cases.
- **Files/Modules Affected:** `backend/api/v1/documents.py`, `backend/ingestion/`, `backend/repositories/`, `tests/integration/`
- **Estimated Complexity:** Medium

## Task #13: Ingestion Service for Parsing, Validation, and Deduplication ✅
- **Branch:** `feature/ingestion-service`
- **Dependencies:** 7, 11
- **Parallelizable With:** 12, 18
- **Description:** Implement ingestion services for TXT, Markdown, HTML, CSV, PDF, and DOCX parsing, plus metadata extraction, deduplication, and safe input validation.
- **Acceptance Criteria:**
- Supported file-type validation is enforced before parsing.
- Content hashing and deduplication rules are applied.
- Metadata extraction populates title, format, language, and source fields when available.
- Service tests cover multiple document types and invalid input.
- **Files/Modules Affected:** `backend/ingestion/`, `backend/ingestion/loaders/`, `backend/ingestion/services.py`, `tests/unit/`
- **Estimated Complexity:** High

## Task #14: Chunking Strategy Registry ✅
- **Branch:** `feature/chunking-strategies`
- **Dependencies:** 13
- **Parallelizable With:** 15, 18
- **Description:** Implement chunking service and strategy registry supporting fixed-size, recursive, markdown-aware, and code-aware chunking with lineage metadata.
- **Acceptance Criteria:**
- Strategy registry selects chunker by config.
- Chunk outputs include document linkage and chunk order.
- Configurable size and overlap are supported.
- Unit tests cover edge cases such as short docs and markdown headers.
- **Files/Modules Affected:** `backend/chunking/`, `backend/models/`, `tests/unit/`
- **Estimated Complexity:** Medium

## Task #15: Embedding Provider Base and OpenAI Adapter ✅
- **Branch:** `feature/embedding-openai-adapter`
- **Dependencies:** 2, 14
- **Parallelizable With:** 14, 16, 18
- **Description:** Create the embedding provider interface, batching behavior, rate-limit hooks, and an initial OpenAI-compatible adapter for chunk vectorization.
- **Acceptance Criteria:**
- Embedding service exposes a provider-agnostic interface.
- OpenAI adapter is configurable from environment settings.
- Batch embedding methods return stable metadata for downstream indexing.
- Tests mock provider calls and verify batching behavior.
- **Files/Modules Affected:** `backend/embedding/`, `backend/core/config.py`, `tests/unit/`
- **Estimated Complexity:** Medium

## Task #16: Vector Store Base and Pinecone Adapter ✅
- **Branch:** `feature/vectorstore-pinecone-adapter`
- **Dependencies:** 2, 14
- **Parallelizable With:** 15, 18
- **Description:** Create the vector store interface and an initial Pinecone adapter for namespace-aware upsert, delete, and similarity search operations.
- **Acceptance Criteria:**
- Vector store abstraction supports create/update/delete/search operations.
- Pinecone adapter handles namespace or index naming consistently.
- Metadata filtering contract is defined for retrieval use.
- Tests mock Pinecone client interactions and error paths.
- **Files/Modules Affected:** `backend/vector_store/`, `backend/vector_store/providers/`, `tests/unit/`
- **Estimated Complexity:** Medium

## Task #17: Index Management API and Service ✅
- **Branch:** `feature/index-management-api`
- **Dependencies:** 8, 14, 15, 16
- **Parallelizable With:** 18, 19
- **Description:** Implement index create/list/detail/rebuild flows with persisted config snapshots and async-ready status transitions.
- **Acceptance Criteria:**
- `POST /indexes`, `GET /indexes`, `GET /indexes/{id}`, and `POST /indexes/{id}/rebuild` exist.
- Index status transitions include `building`, `ready`, and `failed`.
- Config hash and namespace/version metadata are stored.
- Integration tests cover create and rebuild behavior.
- **Files/Modules Affected:** `backend/api/v1/indexes.py`, `backend/vector_store/`, `backend/repositories/index_repository.py`, `tests/integration/`
- **Estimated Complexity:** High

## Task #18: Celery App, Queue Topology, and Worker Bootstrap ✅
- **Branch:** `feature/celery-worker-foundation`
- **Dependencies:** 2, 3, 5
- **Parallelizable With:** 12, 13, 14, 15, 16, 17
- **Description:** Add Celery configuration, worker startup, queue naming, retry defaults, and task registration for `ingest`, `embed`, `eval`, and `index`.
- **Acceptance Criteria:**
- Celery app boots from shared settings.
- Named queues align with `docs/ARCHITECTURE.md` and `docs/LDL.md`.
- Worker process can run locally with Redis broker.
- A smoke test or fixture proves task dispatch works.
- **Files/Modules Affected:** `backend/workers/`, `docker-compose.yml`, `backend/core/config.py`, `tests/`
- **Estimated Complexity:** Medium

## Task #19: Async Ingest to Embed to Index Pipeline ✅
- **Branch:** `feature/async-ingest-index-pipeline`
- **Dependencies:** 12, 13, 14, 15, 16, 17, 18
- **Parallelizable With:** None
- **Description:** Connect document registration, chunk generation, embedding, vector upsert, and document/index status updates into an end-to-end background workflow.
- **Acceptance Criteria:**
- Document ingest can progress from `pending` to `ready` through background tasks.
- Index build jobs persist status and failure details.
- Retry-safe logic avoids duplicate chunk/vector creation on reruns.
- Integration tests cover a full happy-path pipeline with mocks.
- **Files/Modules Affected:** `backend/workers/tasks/`, `backend/ingestion/`, `backend/chunking/`, `backend/embedding/`, `backend/vector_store/`, `tests/integration/`
- **Estimated Complexity:** High

✅ Milestone 3: Ingestion and Indexing Complete

---

## Phase 4 - Retrieval and Generation

## Task #20: Retrieval Service with Vector Search and Filters ✅
- **Branch:** `feature/retrieval-vector-baseline`
- **Dependencies:** 16, 17, 19
- **Parallelizable With:** None
- **Description:** Build the retrieval service for vector search, top-k selection, metadata filters, and source normalization for downstream generation.
- **Acceptance Criteria:**
- Retrieval service accepts index ID, query embedding, filters, and `top_k`.
- Results include source metadata needed for citations.
- Empty-result and backend-failure cases are handled explicitly.
- Unit tests cover filtering and result ordering.
- **Files/Modules Affected:** `backend/retrieval/`, `backend/vector_store/`, `tests/unit/`
- **Estimated Complexity:** Medium

## Task #21: Hybrid Retrieval, BM25, and MMR ✅
- **Branch:** `feature/retrieval-hybrid-mmr`
- **Dependencies:** 20
- **Parallelizable With:** 22, 24
- **Description:** Extend retrieval with hybrid vector plus lexical search, MMR diversification, and configuration hooks for future reranking.
- **Acceptance Criteria:**
- Hybrid retrieval can combine lexical and vector scores.
- MMR option can reduce redundancy in returned chunks.
- Retrieval config is persisted or passed consistently through service APIs.
- Unit tests verify fusion and diversification behavior.
- **Files/Modules Affected:** `backend/retrieval/`, `backend/indexes/` or `backend/vector_store/`, `tests/unit/`
- **Estimated Complexity:** High

## Task #22: Generation Service with Prompt Templates and OpenAI Chat Adapter ✅
- **Branch:** `feature/generation-openai-service`
- **Dependencies:** 2, 20
- **Parallelizable With:** 21, 24
- **Description:** Implement generation service, prompt template registry, token budgeting, and an OpenAI-compatible chat completion adapter.
- **Acceptance Criteria:**
- Generation service accepts prompt template, context, and user question.
- Token budgeting constrains context assembly before model invocation.
- Provider errors are mapped to safe domain errors.
- Unit tests mock LLM responses and failure paths.
- **Files/Modules Affected:** `backend/generation/`, `backend/core/config.py`, `tests/unit/`
- **Estimated Complexity:** Medium

## Task #23: Query API and RAG Response Contract ✅
- **Branch:** `feature/query-api`
- **Dependencies:** 20, 22
- **Parallelizable With:** 24, 25
- **Description:** Implement `POST /query` and optional `POST /rag/query` using retrieval and generation services with response latency and source payloads.
- **Acceptance Criteria:**
- Query endpoints accept documented request payloads.
- Responses include answer text, sources, latency, and optional experiment context.
- Auth and rate limits are enforced.
- API integration tests cover successful query, empty retrieval, and invalid request scenarios.
- **Files/Modules Affected:** `backend/api/v1/query.py`, `backend/api/v1/rag.py`, `backend/retrieval/`, `backend/generation/`, `tests/integration/`
- **Estimated Complexity:** Medium

## Task #24: Realtime Query Streaming and Job Status Channel ✅
- **Branch:** `feature/realtime-query-status`
- **Dependencies:** 18, 23
- **Parallelizable With:** 21, 22, 25
- **Description:** Add realtime features for query streaming and long-running job status updates using WebSockets or Socket.IO-compatible abstractions.
- **Acceptance Criteria:**
- Streaming query responses work for supported providers or gracefully downgrade.
- Background job status updates are exposed over a realtime channel.
- Connection auth and disconnect handling are implemented.
- Integration or contract tests cover connect, message, and completion events.
- **Files/Modules Affected:** `backend/api/realtime/`, `backend/workers/`, `frontend/` or `tests/`
- **Estimated Complexity:** High

## Task #25: Source Citation, Prompt Injection Guardrails, and Response Safety ✅
- **Branch:** `feature/rag-safety-citations`
- **Dependencies:** 23
- **Parallelizable With:** 24
- **Description:** Add citation formatting, document/source traceability, prompt-injection defensive filtering, and safe output handling for RAG responses.
- **Acceptance Criteria:**
- Source chunks are traceable back to documents and included in responses.
- Injection-aware guardrails sanitize or label unsafe retrieved content before prompt assembly.
- Unsafe or malformed model outputs are handled before returning or persisting.
- Tests cover citation mapping and guardrail behavior.
- **Files/Modules Affected:** `backend/generation/`, `backend/retrieval/`, `backend/core/security.py`, `tests/unit/`
- **Estimated Complexity:** High

✅ Milestone 4: RAG Query Flow Complete

---

## Phase 5 - Experiments, Evaluation, and Optimization

## Task #26: Experiments API and Registry Service
- **Branch:** `feature/experiments-registry`
- **Dependencies:** 8, 17, 19
- **Parallelizable With:** None
- **Description:** Implement experiment CRUD, config snapshotting, config hashing, and experiment-run kickoff contracts.
- **Acceptance Criteria:**
- `POST /experiments`, `GET /experiments`, `GET /experiments/{id}`, and `POST /experiments/{id}/run` exist.
- Experiment configs are stored as reproducible JSON/YAML-derived payloads.
- Run creation records queueable status transitions.
- API tests cover create, list, detail, and run kickoff.
- **Files/Modules Affected:** `backend/api/v1/experiments.py`, `backend/experiments/`, `backend/repositories/`, `tests/integration/`
- **Estimated Complexity:** Medium

## Task #27: Evaluation Dataset Generation and Metric Aggregation
- **Branch:** `feature/eval-datasets-metrics`
- **Dependencies:** 20, 22, 26
- **Parallelizable With:** 28, 29
- **Description:** Build evaluation services for synthetic or curated datasets, per-case execution, and aggregate metrics such as relevance, faithfulness, latency, and cost.
- **Acceptance Criteria:**
- Eval service can create or ingest evaluation cases for a run.
- Aggregated metrics persist to `metric_snapshots`.
- Cost and latency are tracked at per-run summary level.
- Unit tests cover metric aggregation and edge cases.
- **Files/Modules Affected:** `backend/evaluation/`, `backend/models/`, `backend/repositories/`, `tests/unit/`
- **Estimated Complexity:** High

## Task #28: Evaluation API, Reports, and Artifact Export
- **Branch:** `feature/evaluation-api-reports`
- **Dependencies:** 18, 26, 27
- **Parallelizable With:** 29
- **Description:** Implement evaluation start/detail/report endpoints, background eval execution, and JSON/HTML artifact export through object storage.
- **Acceptance Criteria:**
- `POST /evaluations`, `GET /evaluations/{id}`, and `GET /evaluations/{id}/report` exist.
- Eval jobs run asynchronously through workers.
- Report artifacts are stored and retrievable safely.
- Integration tests cover evaluation lifecycle and artifact lookup.
- **Files/Modules Affected:** `backend/api/v1/evaluations.py`, `backend/evaluation/`, `backend/workers/tasks/`, `tests/integration/`
- **Estimated Complexity:** High

## Task #29: MLflow Experiment Tracking Integration
- **Branch:** `feature/mlflow-tracking`
- **Dependencies:** 26, 27
- **Parallelizable With:** 28, 30
- **Description:** Add MLflow integration for experiment params, run metrics, and artifact references while keeping tracker usage optional and environment-driven.
- **Acceptance Criteria:**
- MLflow tracking URI and run logging are configurable.
- Experiment and evaluation runs can emit params and metrics to MLflow.
- Tracking failures do not corrupt core experiment persistence.
- Tests mock MLflow client behavior.
- **Files/Modules Affected:** `backend/experiments/tracking/`, `backend/evaluation/`, `backend/core/config.py`, `tests/unit/`
- **Estimated Complexity:** Medium

## Task #30: LangGraph Orchestrator and Optimization Loop
- **Branch:** `feature/langgraph-orchestrator`
- **Dependencies:** 21, 25, 26, 27, 29
- **Parallelizable With:** None
- **Description:** Implement a LangGraph-backed orchestrator for failure analysis, strategy switching, constrained hyperparameter search, and rollback to best-known config.
- **Acceptance Criteria:**
- Orchestrator can propose and execute bounded experiment iterations.
- Failure categories and rollback rules are explicit and testable.
- Strategy choices are persisted or logged with run metadata.
- Unit tests mock LLM/retrieval dependencies and verify decision logic.
- **Files/Modules Affected:** `backend/orchestration/`, `backend/experiments/`, `backend/evaluation/`, `tests/unit/`
- **Estimated Complexity:** High

✅ Milestone 5: Evaluation and Optimization Complete

---

## Phase 6 - Frontend and Product Integrations

## Task #31: Frontend App Shell and Auth Session Flow
- **Branch:** `feature/frontend-shell-auth`
- **Dependencies:** 9, 10, 23
- **Parallelizable With:** None
- **Description:** Create the React/Vite frontend shell, route layout, auth session handling, and shared API client setup for the dashboard.
- **Acceptance Criteria:**
- Frontend app boots with routing and environment configuration.
- Auth-aware API client can attach JWT or API key credentials.
- Protected page layout and loading/error states exist.
- Basic frontend tests cover session guard behavior.
- **Files/Modules Affected:** `frontend/src/`, `frontend/package.json`, `frontend/vite.config.*`, `tests/`
- **Estimated Complexity:** Medium

## Task #32: Frontend Documents and Index Management Pages
- **Branch:** `feature/frontend-documents-indexes`
- **Dependencies:** 12, 17, 31
- **Parallelizable With:** 33, 34
- **Description:** Build dashboard pages for document ingestion status, document detail, index listing, and index rebuild triggers.
- **Acceptance Criteria:**
- Users can view documents, statuses, and indexes from the UI.
- Create/rebuild actions call backend endpoints with proper feedback states.
- Table filters and detail panels reflect backend response contracts.
- Component tests cover empty, loading, and success states.
- **Files/Modules Affected:** `frontend/src/pages/`, `frontend/src/components/`, `frontend/src/api/`
- **Estimated Complexity:** Medium

## Task #33: Frontend Query Playground and Evaluation Views
- **Branch:** `feature/frontend-query-evals`
- **Dependencies:** 23, 28, 31
- **Parallelizable With:** 32, 34
- **Description:** Build query playground, source panel, evaluation summary views, and report links for operators and ML engineers.
- **Acceptance Criteria:**
- Query playground can submit questions and display answer plus sources.
- Evaluation status and metric summaries are viewable in the UI.
- Realtime updates integrate if Task 24 is complete; otherwise polling fallback is used.
- Component tests cover query and evaluation rendering.
- **Files/Modules Affected:** `frontend/src/pages/`, `frontend/src/components/`, `frontend/src/hooks/`
- **Estimated Complexity:** Medium

## Task #34: Notification Integrations with SendGrid and Twilio
- **Branch:** `feature/notifications-sendgrid-twilio`
- **Dependencies:** 28, 31
- **Parallelizable With:** 32, 33, 35
- **Description:** Add optional notification adapters for email and SMS alerts on eval completion, deployment changes, or critical failures.
- **Acceptance Criteria:**
- Notification service supports SendGrid and Twilio adapters behind feature flags.
- Templates or payload builders exist for core event types.
- Failure to send notifications does not break core workflows.
- Tests mock provider APIs and verify event dispatch rules.
- **Files/Modules Affected:** `backend/integrations/notifications/`, `backend/workers/`, `backend/core/config.py`, `tests/unit/`
- **Estimated Complexity:** Medium

## Task #35: Stripe Billing Hooks for Usage Metering
- **Branch:** `feature/stripe-usage-hooks`
- **Dependencies:** 27, 31
- **Parallelizable With:** 34
- **Description:** Add optional Stripe-oriented usage metering hooks for future billing, keeping this task isolated from core MVP behavior because billing is not a product baseline requirement.
- **Acceptance Criteria:**
- Usage events can be emitted from query/eval flows through a billing abstraction.
- Stripe integration is optional and disabled by default.
- No protected core workflow depends on billing being enabled.
- Tests cover event emission and disabled-mode behavior.
- **Files/Modules Affected:** `backend/integrations/billing/`, `backend/query/` or `backend/evaluation/`, `backend/core/config.py`, `tests/unit/`
- **Estimated Complexity:** Medium

✅ Milestone 6: Dashboard and Product Hooks Complete

---

## Phase 7 - Observability, Deployment, and Delivery

## Task #36: Prometheus Metrics, OpenTelemetry Hooks, and Audit Logging
- **Branch:** `feature/observability-and-audit`
- **Dependencies:** 10, 19, 23, 28
- **Parallelizable With:** 37, 39
- **Description:** Add API and worker metrics, trace hooks, and audit logging for sensitive actions such as document access, config changes, and deployment operations.
- **Acceptance Criteria:**
- `/metrics` endpoint or equivalent exporter is available for internal use.
- Request latency, job duration, and failure counters are instrumented.
- Audit logs capture sensitive operations without leaking secrets or raw PII.
- Tests cover metrics registration and audit event generation where practical.
- **Files/Modules Affected:** `backend/api/v1/metrics.py`, `backend/core/telemetry.py`, `backend/core/logging.py`, `tests/`
- **Estimated Complexity:** High

## Task #37: Production Docker Images and Runtime Hardening
- **Branch:** `feature/production-containers`
- **Dependencies:** 3, 18, 36
- **Parallelizable With:** 39, 40
- **Description:** Harden API and worker container images for production with non-root runtime, health checks, and separated commands.
- **Acceptance Criteria:**
- API and worker images build from a production-ready Dockerfile setup.
- Containers run as non-root and expose only required ports.
- Health checks target `/health` and `/ready`.
- Build instructions are updated for local and CI usage.
- **Files/Modules Affected:** `Dockerfile`, `docker-compose.yml`, `scripts/`, `docs/DEPLOYMENT.md`
- **Estimated Complexity:** Medium

## Task #38: GCP Deployment Manifests and Environment Templates
- **Branch:** `feature/gcp-deployment-config`
- **Dependencies:** 37
- **Parallelizable With:** 40
- **Description:** Create GCP-first deployment configuration for VertexOps, including environment templates, service account assumptions, secret references, and baseline cloud runtime docs.
- **Acceptance Criteria:**
- GCP deployment artifacts or manifests exist for API and worker services.
- Environment assumptions are documented for Vertex AI, storage, and observability.
- Secrets are referenced through environment or secret manager patterns.
- Deployment documentation matches the produced configuration.
- **Files/Modules Affected:** `deploy/` or `k8s/`, `docs/DEPLOYMENT.md`, `.env.example`
- **Estimated Complexity:** High

## Task #39: CI/CD Pipeline for Lint, Test, Build, and Deploy
- **Branch:** `feature/ci-cd-pipeline`
- **Dependencies:** 36, 37
- **Parallelizable With:** 38
- **Description:** Implement CI/CD workflows that run linting, unit/integration tests, image builds, and gated deployment steps for `development` and later environments.
- **Acceptance Criteria:**
- CI runs lint and tests on feature branches and `development`.
- Container images build successfully in CI.
- Deployment jobs are separated from test jobs and can be gated.
- Pipeline documentation explains promotion flow.
- **Files/Modules Affected:** `.github/workflows/` or `cloudbuild.yaml`, `scripts/`, `docs/DEPLOYMENT.md`
- **Estimated Complexity:** High

## Task #40: Optional AWS Deployment Parity Pack
- **Branch:** `feature/aws-deployment-parity`
- **Dependencies:** 38, 39
- **Parallelizable With:** None
- **Description:** Add optional AWS deployment examples or Terraform modules for teams that need non-baseline cloud parity, without changing VertexOps' GCP-first defaults.
- **Acceptance Criteria:**
- AWS-specific artifacts are isolated from baseline deployment config.
- GCP remains the documented default path.
- Terraform or deployment templates clearly label AWS support as optional.
- Docs explain scope, assumptions, and differences from the GCP baseline.
- **Files/Modules Affected:** `terraform/aws/` or `deploy/aws/`, `docs/DEPLOYMENT.md`
- **Estimated Complexity:** Medium

✅ Milestone 7: Deployment Pipeline Complete

---

## Phase 8 - Final Quality and Documentation

## Task #41: Unit, Integration, and E2E Quality Sweep
- **Branch:** `feature/test-suites-and-fixtures`
- **Dependencies:** 30, 33, 39
- **Parallelizable With:** 42
- **Description:** Close testing gaps with stable fixtures, endpoint integration coverage, worker-flow tests, and targeted frontend E2E coverage for core operator journeys.
- **Acceptance Criteria:**
- Critical services have deterministic unit tests with mocked external dependencies.
- API integration tests cover auth, ingest, indexing, query, experiments, and evaluations.
- Frontend E2E covers at least login/session, document flow, and query playground.
- Test commands are documented and CI-ready.
- **Files/Modules Affected:** `tests/unit/`, `tests/integration/`, `tests/e2e/`, `frontend/`, `pytest.ini` or equivalent
- **Estimated Complexity:** High

## Task #42: Documentation, Release Checklist, and Task Roadmap Reconciliation
- **Branch:** `feature/docs-and-release-polish`
- **Dependencies:** 38, 39, 41
- **Parallelizable With:** None
- **Description:** Update all implementation-facing docs, release checklists, environment examples, and this roadmap so the repository has a current single source of truth after delivery.
- **Acceptance Criteria:**
- Docs reflect final implemented routes, modules, and deployment paths.
- Release checklist covers migrations, index namespace alignment, secrets, and observability.
- `task.md` is updated to mark completed tasks or scope shifts.
- No stale examples contradict actual code or deployment flow.
- **Files/Modules Affected:** `docs/`, `.env.example`, `README.md`, `task.md`
- **Estimated Complexity:** Medium

✅ Milestone 8: Release Readiness Complete

---

## Recommended Execution Order Summary

1. Complete Tasks 1-5 sequentially to establish the base platform.
2. Parallelize Tasks 6-9, then finish Task 10.
3. Complete Task 11, then split work across Tasks 12-18 in parallel where dependencies allow.
4. Merge Task 19 before beginning retrieval and query tasks.
5. After Task 20, parallelize Tasks 21, 22, and prep for 24; complete Task 23 before tasking realtime and safety layers.
6. Use Tasks 26-30 as the experiments and evaluation lane once the query path is stable.
7. Delay Tasks 31-35 until backend contracts are stable enough to avoid churn in the UI and integrations.
8. Treat Task 40 as optional cloud parity work after the GCP-first deployment path is complete.
9. Do Task 42 last so docs reflect the implemented system rather than the intended system.

## Best Parallel Work Sets

- **Set A:** Tasks 2, 3, 4
- **Set B:** Tasks 6, 7, 8, 9
- **Set C:** Tasks 12, 13, 18
- **Set D:** Tasks 14, 15, 16
- **Set E:** Tasks 21, 22
- **Set F:** Tasks 27, 28, 29
- **Set G:** Tasks 32, 33, 34
- **Set H:** Tasks 36, 37, 39

## Notes for Future "Implement Task #N" Requests

- Each task is scoped so it can be implemented as one feature branch against `development`.
- If a requested task depends on unfinished upstream tasks, implement the dependencies first or explicitly stub the missing contracts inside the same branch.
- When a task affects external providers such as OpenAI, Pinecone, MLflow, SendGrid, Twilio, Stripe, or cloud deployment targets, default to mocked tests and environment-driven configuration.
