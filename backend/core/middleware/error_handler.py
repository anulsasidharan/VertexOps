"""Exception handlers — map domain and framework errors to the API error envelope."""

import logging

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from backend.core.exceptions import (
    ErrorCode,
    ErrorEnvelope,
    VertexOpsError,
)

logger = logging.getLogger(__name__)


async def domain_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Convert any ``VertexOpsError`` subclass to a structured error envelope."""
    assert isinstance(exc, VertexOpsError)
    if exc.status_code >= 500:
        logger.error(
            "domain error: %s",
            exc.message,
            extra={"error_code": exc.error_code, "details": exc.details},
            exc_info=exc,
        )
    else:
        logger.info(
            "client error: %s",
            exc.message,
            extra={"error_code": exc.error_code, "http_status": exc.status_code},
        )
    return JSONResponse(
        status_code=exc.status_code,
        content=exc.to_envelope().model_dump(),
    )


async def request_validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Convert Pydantic request-body validation errors to VALIDATION_ERROR envelope."""
    errors = exc.errors()
    details = {"fields": [{"loc": list(e["loc"]), "msg": e["msg"]} for e in errors]}
    logger.info("request validation error", extra={"validation_errors": errors})
    envelope = ErrorEnvelope.build(
        ErrorCode.VALIDATION_ERROR,
        "Request validation failed.",
        details,
    )
    return JSONResponse(status_code=422, content=envelope.model_dump())


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Catch-all for unhandled exceptions — return INTERNAL_ERROR without leaking details."""
    logger.exception("unhandled exception on %s %s", request.method, request.url.path)
    envelope = ErrorEnvelope.build(ErrorCode.INTERNAL_ERROR, "An internal error occurred.")
    return JSONResponse(status_code=500, content=envelope.model_dump())
