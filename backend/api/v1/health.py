"""Health and readiness endpoints."""

from fastapi import APIRouter
from pydantic import BaseModel

from backend.core.db import check_db_connectivity

router = APIRouter()


class HealthResponse(BaseModel):
    status: str


class ReadinessResponse(BaseModel):
    status: str
    checks: dict


@router.get("/health", response_model=HealthResponse, summary="Liveness probe")
async def health() -> HealthResponse:
    """Returns 200 when the process is alive."""
    return HealthResponse(status="ok")


@router.get("/ready", response_model=ReadinessResponse, summary="Readiness probe")
async def ready() -> ReadinessResponse:
    """Returns 200 when all critical dependencies are reachable."""
    db_ok = await check_db_connectivity()
    all_ok = db_ok
    return ReadinessResponse(
        status="ok" if all_ok else "degraded",
        checks={"database": "ok" if db_ok else "unreachable"},
    )
