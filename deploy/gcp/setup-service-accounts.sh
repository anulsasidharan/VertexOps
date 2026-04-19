#!/usr/bin/env bash
# Provision GCP service accounts and IAM bindings required by VertexOps.
#
# Usage:
#   export GCP_PROJECT_ID=my-project
#   ./deploy/gcp/setup-service-accounts.sh
#
# Run once per GCP project. Requires owner or IAM admin permissions.
set -euo pipefail

PROJECT="${GCP_PROJECT_ID:?GCP_PROJECT_ID must be set}"
REGION="${VERTEX_AI_LOCATION:-us-central1}"

echo "==> Enabling required GCP APIs..."
gcloud services enable \
  aiplatform.googleapis.com \
  run.googleapis.com \
  cloudbuild.googleapis.com \
  secretmanager.googleapis.com \
  artifactregistry.googleapis.com \
  monitoring.googleapis.com \
  cloudtrace.googleapis.com \
  --project="${PROJECT}"

echo "==> Creating Artifact Registry repository..."
gcloud artifacts repositories create vertexops \
  --repository-format=docker \
  --location="${REGION}" \
  --description="VertexOps container images" \
  --project="${PROJECT}" || true

echo "==> Creating API service account..."
gcloud iam service-accounts create vertexops-api \
  --display-name="VertexOps API" \
  --project="${PROJECT}" || true

echo "==> Creating Worker service account..."
gcloud iam service-accounts create vertexops-worker \
  --display-name="VertexOps Worker" \
  --project="${PROJECT}" || true

API_SA="vertexops-api@${PROJECT}.iam.gserviceaccount.com"
WORKER_SA="vertexops-worker@${PROJECT}.iam.gserviceaccount.com"

echo "==> Binding IAM roles to API service account..."
for role in \
  roles/aiplatform.user \
  roles/secretmanager.secretAccessor \
  roles/cloudtrace.agent \
  roles/monitoring.metricWriter \
  roles/storage.objectViewer; do
  gcloud projects add-iam-policy-binding "${PROJECT}" \
    --member="serviceAccount:${API_SA}" \
    --role="${role}" \
    --quiet
done

echo "==> Binding IAM roles to Worker service account..."
for role in \
  roles/aiplatform.user \
  roles/secretmanager.secretAccessor \
  roles/cloudtrace.agent \
  roles/monitoring.metricWriter \
  roles/storage.objectAdmin; do
  gcloud projects add-iam-policy-binding "${PROJECT}" \
    --member="serviceAccount:${WORKER_SA}" \
    --role="${role}" \
    --quiet
done

echo "==> Granting Cloud Build service account permission to deploy..."
CLOUDBUILD_SA="$(gcloud projects describe "${PROJECT}" --format='value(projectNumber)')@cloudbuild.gserviceaccount.com"
gcloud projects add-iam-policy-binding "${PROJECT}" \
  --member="serviceAccount:${CLOUDBUILD_SA}" \
  --role="roles/run.admin" \
  --quiet
gcloud projects add-iam-policy-binding "${PROJECT}" \
  --member="serviceAccount:${CLOUDBUILD_SA}" \
  --role="roles/iam.serviceAccountUser" \
  --quiet

echo ""
echo "==> Done. Next steps:"
echo "    1. Store secrets in Secret Manager:"
echo "       gcloud secrets create vertexops-jwt-secret --data-file=<(openssl rand -hex 32)"
echo "       gcloud secrets create vertexops-api-key-pepper --data-file=<(openssl rand -hex 16)"
echo "       gcloud secrets create vertexops-db-url --data-file=- <<< 'postgresql+asyncpg://...'"
echo "    2. Submit a build: gcloud builds submit --config deploy/gcp/cloudbuild.yaml"
