# VertexOps — Deployment Guide

Aligned with [CLAUDE.md](../CLAUDE.md). GCP (Cloud Run + Cloud Build) is the primary deployment target. AWS is supported as optional parity (see §7).

---

## Table of Contents

1. [Topology](#1-topology)
2. [Local Development](#2-local-development)
3. [Production Containers](#3-production-containers)
4. [Environment Variable Reference](#4-environment-variable-reference)
5. [GCP Deployment — Cloud Run](#5-gcp-deployment--cloud-run)
6. [CI/CD — GitHub Actions](#6-cicd--github-actions)
7. [AWS Deployment (Optional Parity)](#7-aws-deployment-optional-parity)
8. [Operations Checklist](#8-operations-checklist)
9. [Related Documents](#9-related-documents)

---

## 1. Topology

```mermaid
flowchart LR
  subgraph clients
    U[Users / Dashboard]
  end
  subgraph GCP Cloud Run
    API[vertexops-api]
    WRK[vertexops-worker]
  end
  subgraph data
    PG[(Cloud SQL PostgreSQL)]
    RD[(Memorystore Redis)]
    VDB[(Pinecone / Vertex Matching Engine)]
    OBJ[(GCS Bucket)]
  end
  subgraph observability
    PROM[Prometheus /metrics]
    OTEL[Cloud Trace / OTLP]
    LOG[Cloud Logging]
  end
  U --> API
  API --> PG
  API --> VDB
  API --> OBJ
  API --> PROM
  API --> OTEL
  WRK --> PG & VDB & OBJ & RD
  API --> RD
```

---

## 2. Local Development

### 2.1 Python environment

Dependencies are declared in `pyproject.toml` and locked in `uv.lock`. Use **[uv](https://docs.astral.sh/uv/)** to create `.venv`:

```bash
uv sync --all-groups          # app + dev tools (pytest, ruff, …)
uv sync                       # runtime only
```

Copy `.env.example` → `.env` and set the required variables (see §4). Never commit `.env`.

### 2.2 Docker Compose

```bash
docker compose up -d postgres redis       # backing services only
docker compose up -d                      # API + backing services
docker compose --profile worker up -d worker   # also start Celery worker
docker compose logs -f api                # follow API logs
docker compose down -v                    # stop and remove volumes
```

#### Service inventory

| Service | Container | Image | Host port | Profile |
|---------|-----------|-------|-----------|---------|
| `postgres` | `vertexops_postgres` | `postgres:16-alpine` | 5432 | default |
| `redis` | `vertexops_redis` | `redis:7-alpine` | 6379 | default |
| `api` | `vertexops_api` | built `--target api` | 8000 | default |
| `worker` | `vertexops_worker` | built `--target worker` | — | `worker` |

#### Connection URLs

| Context | DATABASE_URL | REDIS_URL |
|---------|-------------|-----------|
| Host machine | `postgresql+asyncpg://vertexops:vertexops@localhost:5432/vertexops` | `redis://localhost:6379/0` |
| Container-to-container | `postgresql+asyncpg://vertexops:vertexops@postgres:5432/vertexops` | `redis://redis:6379/0` |

### 2.3 Migrations and bootstrap user

```bash
uv run alembic upgrade head
uv run python -m scripts.bootstrap_dev_user   # dev admin: admin@localhost / changeme
```

---

## 3. Production Containers

The `Dockerfile` defines three named targets:

| Target | Purpose | Default CMD |
|--------|---------|-------------|
| `runtime-base` | Shared base — non-root user, runtime libs, app code | — |
| `api` | FastAPI + Uvicorn | `uvicorn backend.main:app --host 0.0.0.0 --port 8000` |
| `worker` | Celery background task processor | `celery -A backend.workers.celery_app worker ...` |

Build both images:

```bash
# Using the helper script
IMAGE_REPO=us-central1-docker.pkg.dev/my-project/vertexops \
  IMAGE_TAG=$(git rev-parse --short HEAD) \
  ./scripts/docker-build.sh --push

# Or directly
docker build --target api   -t vertexops-api:latest .
docker build --target worker -t vertexops-worker:latest .
```

**Security hardening:**
- Containers run as non-root `appuser` (uid 1001)
- No build tools in the runtime layer
- Secrets injected via environment variables or Secret Manager CSI; never baked into the image
- Health checks: API → `GET /api/v1/health`; Worker → `celery inspect ping`

---

## 4. Environment Variable Reference

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `APP_ENV` | | `development` | `development` / `staging` / `production` |
| `DEBUG` | | `false` | Enable SQL query logging |
| `DATABASE_URL` | | localhost default | Async PostgreSQL connection string |
| `REDIS_URL` | | `redis://localhost:6379/0` | Redis connection |
| `REDIS_BROKER_URL` | | `redis://localhost:6379/1` | Celery broker |
| `CELERY_RESULT_BACKEND` | | `redis://localhost:6379/2` | Celery results |
| `JWT_SECRET_KEY` | **REQUIRED** | — | JWT signing secret (`openssl rand -hex 32`) |
| `API_KEY_PEPPER` | **REQUIRED** | — | API key HMAC pepper (`openssl rand -hex 16`) |
| `OPENAI_API_KEY` | | — | Required for OpenAI embeddings / chat |
| `GCP_PROJECT_ID` | | — | Required for Vertex AI or GCS |
| `VERTEX_AI_LOCATION` | | `us-central1` | Vertex AI region |
| `PINECONE_API_KEY` | | — | Required for Pinecone vector store |
| `GCS_BUCKET_NAME` | | — | GCS bucket for documents and artifacts |
| `METRICS_ENABLED` | | `false` | Expose `GET /api/v1/metrics` for Prometheus |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | | — | OTLP gRPC endpoint for Cloud Trace |
| `LOG_LEVEL` | | `INFO` | `DEBUG` / `INFO` / `WARNING` / `ERROR` |
| `MLFLOW_ENABLED` | | `false` | Enable MLflow experiment tracking |
| `MLFLOW_TRACKING_URI` | | — | MLflow server URI |
| `NOTIFICATIONS_ENABLED` | | `false` | Enable SendGrid / Twilio notifications |
| `SENDGRID_API_KEY` | | — | SendGrid API key |
| `TWILIO_ACCOUNT_SID` | | — | Twilio SID |
| `STRIPE_METERING_ENABLED` | | `false` | Enable Stripe usage metering |
| `STRIPE_API_KEY` | | — | Stripe API key |

See `.env.example` for the full annotated list.

---

## 5. GCP Deployment — Cloud Run

### 5.1 Prerequisites

```bash
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
```

### 5.2 First-time infrastructure setup

```bash
export GCP_PROJECT_ID=your-project-id
export VERTEX_AI_LOCATION=us-central1
./deploy/gcp/setup-service-accounts.sh
```

This script:
- Enables required APIs (AI Platform, Cloud Run, Cloud Build, Secret Manager, Artifact Registry, Monitoring, Cloud Trace)
- Creates `vertexops-api` and `vertexops-worker` service accounts with least-privilege roles
- Grants Cloud Build the ability to deploy to Cloud Run

### 5.3 Store secrets in Secret Manager

```bash
# Required secrets
gcloud secrets create vertexops-jwt-secret \
  --data-file=<(openssl rand -hex 32) --project=$GCP_PROJECT_ID
gcloud secrets create vertexops-api-key-pepper \
  --data-file=<(openssl rand -hex 16) --project=$GCP_PROJECT_ID
gcloud secrets create vertexops-db-url \
  --data-file=- <<< "postgresql+asyncpg://user:pass@/vertexops?host=/cloudsql/PROJECT:REGION:INSTANCE"
gcloud secrets create vertexops-redis-url \
  --data-file=- <<< "redis://10.x.x.x:6379/0"
```

### 5.4 Deploy via Cloud Build

```bash
gcloud builds submit \
  --config=deploy/gcp/cloudbuild.yaml \
  --substitutions=_REGION=us-central1,_GCP_PROJECT_ID=$GCP_PROJECT_ID \
  .
```

The pipeline:
1. Runs unit tests
2. Builds and pushes `vertexops-api` and `vertexops-worker` images in parallel
3. Executes DB migration as a Cloud Run Job (`vertexops-migrate`)
4. Deploys API with `--no-traffic`, then shifts traffic to the new revision
5. Deploys Worker

### 5.5 Cloud Run service manifests

- **`deploy/gcp/cloud-run-api.yaml`** — API service (public ingress, min 1 instance, 2 CPU / 2 GiB)
- **`deploy/gcp/cloud-run-worker.yaml`** — Worker service (internal ingress, 4 CPU / 4 GiB)

Apply directly with:

```bash
# Substitute variables, then apply
envsubst < deploy/gcp/cloud-run-api.yaml | \
  gcloud run services replace - --region=$REGION
```

### 5.6 Observability

- **Prometheus:** Set `METRICS_ENABLED=true`; scrape `GET /api/v1/metrics` from a GCP-internal Prometheus instance or use a Cloud Monitoring integration.
- **OpenTelemetry:** Set `OTEL_EXPORTER_OTLP_ENDPOINT` to a GCP-hosted OTLP collector forwarding to Cloud Trace.
- **Logs:** All logs are structured JSON; Cloud Logging picks them up automatically from Cloud Run stdout.

---

## 6. CI/CD — GitHub Actions

See `.github/workflows/` for the full pipeline definition.

| Workflow | Trigger | Steps |
|----------|---------|-------|
| `ci.yml` | PR to `development` or `main` | Lint (ruff), unit tests, type check (mypy) |
| `build-deploy.yml` | Push to `development` | Build images → push to Artifact Registry → deploy to Cloud Run (staging) |
| `build-deploy.yml` | Push tag `v*` | Same + deploy to production with manual approval gate |

Required GitHub secrets:

| Secret | Description |
|--------|-------------|
| `GCP_PROJECT_ID` | GCP project |
| `GCP_REGION` | Deployment region |
| `GCP_SA_KEY` | JSON key for a CI service account with Artifact Registry + Cloud Run permissions |
| `ARTIFACT_REGISTRY_REPO` | Artifact Registry repo name |

---

## 7. AWS Deployment (Optional Parity)

AWS support is provided as an optional parity pack in `deploy/aws/`. GCP remains the documented and tested baseline.

See [`deploy/aws/README.md`](../deploy/aws/README.md) for full instructions. The AWS pack includes:

- Terraform modules for ECS (Fargate), RDS PostgreSQL, ElastiCache Redis, ECR, and VPC
- ECS task definitions for API and Worker
- ALB + WAF configuration

**GCP is the primary target.** AWS parity is community-supported and not gated in CI by default.

---

## 8. Operations Checklist

- [ ] `alembic upgrade head` applied (or `vertexops-migrate` Cloud Run Job executed)
- [ ] `JWT_SECRET_KEY` and `API_KEY_PEPPER` rotated from dev defaults
- [ ] Secrets are stored in Secret Manager, not baked into images or env files
- [ ] Vector index namespace matches the release tag / config hash
- [ ] `METRICS_ENABLED=true` and Prometheus scrape target configured
- [ ] `OTEL_EXPORTER_OTLP_ENDPOINT` set if Cloud Trace integration is required
- [ ] Backup policy configured for Cloud SQL and GCS bucket
- [ ] Alerts set for error rate > 1% and P95 latency > 500 ms

---

## 9. Related Documents

- [ARCHITECTURE.md](ARCHITECTURE.md)
- [API_SPEC.md](API_SPEC.md)
- [DB_SCHEMA.md](DB_SCHEMA.md)
- [PRD.md](PRD.md)
- [CLAUDE.md](../CLAUDE.md)
