#!/usr/bin/env bash
# Build and optionally push API and worker Docker images.
#
# Usage:
#   ./scripts/docker-build.sh                     # build both, tag :latest
#   ./scripts/docker-build.sh --push              # build and push to registry
#   IMAGE_REPO=gcr.io/my-project/vertexops \
#     IMAGE_TAG=abc1234 ./scripts/docker-build.sh --push
#
# Environment variables:
#   IMAGE_REPO  — registry prefix  (default: vertexops)
#   IMAGE_TAG   — image tag        (default: latest)
#   PUSH        — set to "1" to push after build (or pass --push flag)

set -euo pipefail

REPO="${IMAGE_REPO:-vertexops}"
TAG="${IMAGE_TAG:-latest}"
PUSH="${PUSH:-0}"

for arg in "$@"; do
  [[ "$arg" == "--push" ]] && PUSH=1
done

API_IMAGE="${REPO}-api:${TAG}"
WORKER_IMAGE="${REPO}-worker:${TAG}"

echo "==> Building API image: ${API_IMAGE}"
docker build \
  --target api \
  --tag "${API_IMAGE}" \
  --build-arg BUILDKIT_INLINE_CACHE=1 \
  .

echo "==> Building Worker image: ${WORKER_IMAGE}"
docker build \
  --target worker \
  --tag "${WORKER_IMAGE}" \
  --build-arg BUILDKIT_INLINE_CACHE=1 \
  .

if [[ "${PUSH}" == "1" ]]; then
  echo "==> Pushing ${API_IMAGE}"
  docker push "${API_IMAGE}"
  echo "==> Pushing ${WORKER_IMAGE}"
  docker push "${WORKER_IMAGE}"
fi

echo "==> Done. Images: ${API_IMAGE}, ${WORKER_IMAGE}"
