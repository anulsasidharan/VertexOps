"""API v1 — aggregates all route modules."""

from fastapi import APIRouter

from backend.api.v1 import auth, documents, health, indexes, query

router = APIRouter()

router.include_router(health.router, tags=["health"])
router.include_router(auth.router, prefix="/auth", tags=["auth"])
router.include_router(documents.router, prefix="/documents", tags=["documents"])
router.include_router(indexes.router, prefix="/indexes", tags=["indexes"])
router.include_router(query.router, tags=["query"])
