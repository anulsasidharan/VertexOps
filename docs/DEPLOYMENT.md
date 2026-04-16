# VertexOps — Deployment Guide

> **Specification:** How to run and ship **VertexOps** in development and production, aligned with [CLAUDE.md](../CLAUDE.md). Adjust service names and paths to match the repository once implementation exists.

---

## 1. Topology

```mermaid
flowchart LR
  subgraph clients
    U[Users_CLI_Dashboard]
  end
  subgraph cluster
    API[FastAPI_API]
    WRK[Background_workers]
  end
  subgraph data
    PG[(PostgreSQL)]
    RD[(Redis_optional)]
    VDB[(Vector_database)]
    OBJ[(Object_storage)]
  end
  U --> API
  API --> PG
  API --> VDB
  API --> OBJ
  WRK --> PG
  WRK --> VDB
  WRK --> OBJ
  API --> RD
  WRK --> RD
```

---

## 2. Local development

### 2.1 Python environment

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and set variables (see §4). Never commit secrets.

### 2.2 Docker Compose

The repository ships a `docker-compose.yml` at the project root. All services
are defined there and can be started with:

```bash
docker compose up -d            # start all services
docker compose up -d postgres redis  # backing services only (no API)
docker compose logs -f api      # follow API logs
docker compose down -v          # stop and remove volumes
```

#### Service inventory

| Service | Container name | Image | Host port | Profile | Role |
|---------|----------------|-------|-----------|---------|------|
| `api` | `vertexops_api` | built from `Dockerfile` | `8000` | _(default)_ | FastAPI + Uvicorn |
| `postgres` | `vertexops_postgres` | `postgres:16-alpine` | `5432` | _(default)_ | Metadata DB |
| `redis` | `vertexops_redis` | `redis:7-alpine` | `6379` | _(default)_ | Broker + rate-limit cache |
| `worker` | `vertexops_worker` | same image as `api` | — | `worker` | Celery background tasks (queues wired in Task #18) |

The `worker` service uses a Docker Compose [profile](https://docs.docker.com/compose/profiles/) so it
is **not** started by default. Start it explicitly when needed:

```bash
docker compose --profile worker up -d worker
```

> **Production note:** avoid publishing `5432` / `6379` in production compose
> overlays. Use an internal network and keep the DB/Redis ports private.

#### Connection URLs

| Context | `DATABASE_URL` | `REDIS_URL` |
|---------|----------------|-------------|
| **Host machine** (IDE / CLI) | `postgresql+asyncpg://vertexops:vertexops@localhost:5432/vertexops` | `redis://localhost:6379/0` |
| **Container-to-container** | `postgresql+asyncpg://vertexops:vertexops@postgres:5432/vertexops` | `redis://redis:6379/0` |

The `api` and `worker` services override these automatically via the
`x-app-env` YAML anchor in `docker-compose.yml`; host-side `.env` values
are not needed inside containers.

---

## 3. Production containers

- **API image:** non-root user, `uvicorn` with production worker model (e.g. gunicorn + uvicorn workers) as appropriate.
- **Worker image:** same codebase, different command; listen on dedicated queues (`ingest`, `embed`, `eval`).
- **Dashboard image (optional):** static build served by CDN or Node static host.

Health checks should call `/health` and `/ready` per [API_SPEC.md](API_SPEC.md).

---

## 4. Environment variable categories

Document exact names in `.env.example` in the codebase. Groups:

| Group | Examples |
|-------|-----------|
| **App** | `APP_ENV`, `LOG_LEVEL`, `API_PREFIX` |
| **Database** | `DATABASE_URL` |
| **Redis** | `REDIS_URL`, `CELERY_BROKER_URL`, `CELERY_RESULT_BACKEND` |
| **Auth** | `JWT_SECRET`, token TTLs, `API_KEY_PEPPER` |
| **Object storage** | `S3_BUCKET`, `GCS_BUCKET`, `AZURE_CONTAINER`, credentials via env or workload identity |
| **LLM** | `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `GOOGLE_API_KEY`, model defaults |
| **Embeddings** | Provider keys and default model id |
| **Vector DB** | Pinecone API key/index; Qdrant URL; Chroma path/host; Weaviate URL |
| **Experiments** | `MLFLOW_TRACKING_URI`, `WANDB_API_KEY` |
| **Observability** | `OTEL_EXPORTER_OTLP_ENDPOINT`, `PROMETHEUS_MULTIPROC_DIR` |

---

## 5. Kubernetes (optional)

- **Deployments:** `autorag-api`, `autorag-worker` with HPA on CPU or request rate.
- **Jobs:** one-off index rebuild or migration tasks.
- **Secrets:** mounted from cloud secret manager CSI or external-secrets operator.
- **Ingress:** TLS termination at load balancer; rate limiting at edge when available.

Manifests may live under `k8s/`; keep them generic across clouds where possible.

---

## 6. Terraform / cloud IaC

- Modules for **AWS**, **GCP**, or **Azure**: network, managed Postgres, Redis, object storage, GKE/EKS/AKS cluster, IAM.
- Pin provider versions; separate `dev` / `staging` / `prod` workspaces.

---

## 7. CI/CD

- Lint (ruff), unit tests, build images, push to registry, deploy via Helm or `kubectl apply`.
- Gate production on eval regression thresholds when automated.

---

## 8. Operations checklist

- [ ] Migrations applied (`alembic upgrade head` or equivalent)
- [ ] Vector index namespace matches release tag
- [ ] Secrets rotated and not present in logs
- [ ] Prometheus scrapes `/metrics` if enabled
- [ ] Backup policy for Postgres and object storage

---

## 9. Related documents

- [ARCHITECTURE.md](ARCHITECTURE.md)
- [API_SPEC.md](API_SPEC.md)
- [PRD.md](PRD.md)
- [CLAUDE.md](../CLAUDE.md)
