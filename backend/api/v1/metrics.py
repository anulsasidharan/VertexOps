"""/metrics — Prometheus scrape endpoint (internal; not exposed publicly in production)."""

from fastapi import APIRouter, HTTPException, Response
from fastapi.responses import PlainTextResponse

from backend.core.config import get_settings
from backend.core.telemetry import get_metrics_output

router = APIRouter()


@router.get(
    "/metrics",
    response_class=PlainTextResponse,
    include_in_schema=False,  # keep off public Swagger
    tags=["observability"],
)
async def prometheus_metrics() -> Response:
    """Prometheus scrape endpoint.

    Returns 404 when METRICS_ENABLED=false so production clusters can
    control exposure without code changes.
    """
    settings = get_settings()
    if not settings.metrics_enabled:
        raise HTTPException(status_code=404, detail="Metrics not enabled.")
    body, content_type = get_metrics_output()
    return Response(content=body, media_type=content_type)
