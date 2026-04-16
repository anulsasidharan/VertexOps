"""API v1 — aggregates all route modules."""

from fastapi import APIRouter

from backend.api.v1 import health

router = APIRouter()

router.include_router(health.router, tags=["health"])

# Future routers (added in later tasks):
# from backend.api.v1 import documents, indexes, query, experiments, evaluations, metrics, auth
# router.include_router(documents.router, prefix="/documents", tags=["documents"])
# router.include_router(indexes.router, prefix="/indexes", tags=["indexes"])
# router.include_router(query.router, prefix="/query", tags=["query"])
# router.include_router(experiments.router, prefix="/experiments", tags=["experiments"])
# router.include_router(evaluations.router, prefix="/evaluations", tags=["evaluations"])
# router.include_router(metrics.router, prefix="/metrics", tags=["metrics"])
# router.include_router(auth.router, prefix="/auth", tags=["auth"])
