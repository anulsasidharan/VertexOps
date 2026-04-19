# VertexOps Release Checklist

Use this checklist before promoting any build from `development` to a production-like environment.

---

## 1. Database and Migrations

- [ ] Run `alembic upgrade head` against the target database and confirm zero errors.
- [ ] Verify `alembic current` reports the expected head revision.
- [ ] Confirm `alembic history` shows all migrations in order (`0001` → `0002` → `0003` → `0004`).
- [ ] Test `alembic downgrade -1` and `alembic upgrade head` round-trip on a staging copy.
- [ ] Check for any data migrations that need to run separately (seed data, index bootstrapping).

---

## 2. Secrets and Environment Variables

- [ ] `JWT_SECRET_KEY` is set to a cryptographically random value (`openssl rand -hex 32`).
- [ ] `API_KEY_PEPPER` is set to a unique random value per environment (`openssl rand -hex 16`).
- [ ] `DATABASE_URL` points to the correct PostgreSQL host, database, and credentials.
- [ ] `REDIS_URL` points to the correct Redis instance.
- [ ] `APP_ENV` is set to `production` (disables debug features, enforces stricter validation).
- [ ] `OPENAI_API_KEY` is set if using OpenAI embeddings or chat completions.
- [ ] `GCP_PROJECT_ID` and `VERTEX_AI_LOCATION` are set if using Vertex AI or GCS.
- [ ] `GCP_SERVICE_ACCOUNT_KEY` or workload identity is configured for GCP access.
- [ ] `PINECONE_API_KEY` and `PINECONE_ENVIRONMENT` are set if using Pinecone.
- [ ] `STORAGE_BACKEND` is set to `gcs` in production (not `local`).
- [ ] `GCS_BUCKET_NAME` points to the correct GCS bucket.
- [ ] `SENDGRID_API_KEY` is set if email notifications are enabled.
- [ ] `TWILIO_ACCOUNT_SID` / `TWILIO_AUTH_TOKEN` are set if SMS notifications are enabled.
- [ ] `STRIPE_API_KEY` is set if billing metering is enabled.
- [ ] `MLFLOW_TRACKING_URI` is configured if MLflow experiment tracking is enabled.
- [ ] No secrets are committed to version control or present in container images.

---

## 3. Vector Index and Namespace Alignment

- [ ] Pinecone index name and namespace match the values in `index_config` for all production indexes.
- [ ] Pinecone index dimension matches the embedding model dimension (e.g., `1536` for `text-embedding-ada-002`).
- [ ] Existing index records in PostgreSQL have a valid `namespace` and `config_hash`.
- [ ] Any indexes with `status = "failed"` have been investigated and remediated before release.
- [ ] After a namespace change or embedding model change, trigger a full index rebuild via `POST /indexes/{id}/rebuild`.

---

## 4. Observability and Alerting

- [ ] `METRICS_ENABLED=true` and `/api/v1/metrics` is scrape-accessible (internal network only).
- [ ] Prometheus targets are updated to include the new API instance(s).
- [ ] GCP Cloud Logging is receiving structured JSON logs (verify in Cloud Logging console).
- [ ] Alerting rules are configured for:
  - Error rate > 1% (5-minute window)
  - P95 API latency > 500ms
  - Worker task failure rate > 0
  - Deployment failures in CI/CD pipeline
- [ ] Audit log sink is active and capturing sensitive operations (document access, config changes).

---

## 5. Container Images and Deployment

- [ ] API and Worker images are built from the production Dockerfile target (`--target production`).
- [ ] Images run as non-root user (`uid=1001`).
- [ ] Health check endpoints (`/api/v1/health`, `/api/v1/ready`) return `200` in the deployed environment.
- [ ] Container resource limits (CPU, memory) are set appropriately for the workload.
- [ ] Secrets are injected via environment or GCP Secret Manager — never baked into the image.
- [ ] Container registry image tags match the deployed git SHA or version tag.

---

## 6. CI/CD Pipeline

- [ ] All GitHub Actions workflows pass on the release commit.
- [ ] `ruff check .` passes with zero violations.
- [ ] `pytest` (unit + integration) passes with no failures (excluding known pre-existing issues).
- [ ] Container build step completes successfully in CI.
- [ ] Deployment step is gated and requires a manual approval or specific branch trigger.

---

## 7. API and Route Verification

- [ ] `GET /api/v1/health` → `200 OK` with `{"status": "ok"}`.
- [ ] `GET /api/v1/ready` → `200 OK` with all dependency checks passing.
- [ ] `POST /api/v1/auth/token` returns a valid JWT for a known user.
- [ ] At least one protected endpoint returns `401` when called without credentials.
- [ ] Rate limiting returns `429` when the configured threshold is exceeded.
- [ ] OpenAPI schema is served at `/openapi.json` (development) or disabled in strict production.

---

## 8. Rollback Plan

- [ ] Previous container image tags are retained in the registry for immediate rollback.
- [ ] `alembic downgrade -1` has been tested and is known-safe for the current migration.
- [ ] Celery task queue is drained before deploying a new worker image to avoid incompatible task signatures.
- [ ] Feature flags (if used) can disable new functionality without redeployment.
- [ ] Incident response runbook is accessible to the on-call team.

---

## 9. Post-Deployment Smoke Tests

Run after each production deployment:

```bash
# Liveness
curl -sf https://<host>/api/v1/health | jq .

# Readiness
curl -sf https://<host>/api/v1/ready | jq .

# Auth
TOKEN=$(curl -sf -X POST https://<host>/api/v1/auth/token \
  -H "Content-Type: application/json" \
  -d '{"email":"<admin-email>","password":"<admin-password>"}' | jq -r .access_token)

# Protected endpoint
curl -sf https://<host>/api/v1/documents \
  -H "Authorization: Bearer $TOKEN" | jq .total
```

---

**Document version:** 1.0  
**Applies to:** VertexOps Phase 8 and beyond
