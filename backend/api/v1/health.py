"""Health and readiness endpoints — placeholder bodies for Task #10."""

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class HealthResponse(BaseModel):
    status: str


@router.get("/health", response_model=HealthResponse, summary="Liveness probe")
async def health() -> HealthResponse:
    """Returns 200 when the process is alive."""
    return HealthResponse(status="ok")


@router.get("/ready", response_model=HealthResponse, summary="Readiness probe")
async def ready() -> HealthResponse:
    """Returns 200 when the service is ready to handle traffic.

    Full dependency checks (DB, Redis) are added in Task #10.
    """
    return HealthResponse(status="ok")
