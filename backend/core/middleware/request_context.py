"""Request context middleware — injects request ID and auth subject placeholder."""

import logging
import time
import uuid
from typing import Awaitable, Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from backend.core.logging import auth_subject_var, request_id_var

logger = logging.getLogger(__name__)

# Header names
_REQUEST_ID_HEADER = "X-Request-ID"
_REQUEST_ID_RESPONSE_HEADER = "X-Request-ID"


class RequestContextMiddleware(BaseHTTPMiddleware):
    """Populate per-request context vars and add ``X-Request-ID`` to responses.

    - Reads ``X-Request-ID`` from the incoming request; generates a UUID4 if
      absent.
    - Stores the ID in ``request_id_var`` so the JSON log formatter can attach
      it to every log record emitted during that request.
    - Stores ``auth_subject_var`` as a placeholder (populated by the auth
      dependency in Task #9).
    - Logs a structured line at the start and end of every request.
    """

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        # Resolve or generate request ID
        req_id = request.headers.get(_REQUEST_ID_HEADER) or str(uuid.uuid4())

        # Set context vars (scoped to this coroutine / asyncio task)
        token_req = request_id_var.set(req_id)
        token_auth = auth_subject_var.set(None)  # auth dependency fills this later

        start_ns = time.perf_counter_ns()
        logger.info(
            "request started",
            extra={
                "http_method": request.method,
                "http_path": request.url.path,
                "client_host": request.client.host if request.client else None,
            },
        )

        try:
            response = await call_next(request)
        finally:
            elapsed_ms = (time.perf_counter_ns() - start_ns) / 1_000_000
            logger.info(
                "request finished",
                extra={
                    "http_method": request.method,
                    "http_path": request.url.path,
                    "http_status": response.status_code if "response" in dir() else 500,
                    "duration_ms": round(elapsed_ms, 2),
                },
            )
            request_id_var.reset(token_req)
            auth_subject_var.reset(token_auth)

        response.headers[_REQUEST_ID_RESPONSE_HEADER] = req_id
        return response
