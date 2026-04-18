"""FastAPI rate-limit dependency factory."""

import logging

from fastapi import Depends, Request, Response

from backend.core.config import get_settings
from backend.core.exceptions import RateLimitError
from backend.core.rate_limit import DEFAULT_POLICY, RateLimitPolicy, get_rate_limiter

logger = logging.getLogger(__name__)

_HEADER_LIMIT = "X-RateLimit-Limit"
_HEADER_REMAINING = "X-RateLimit-Remaining"
_HEADER_RESET = "X-RateLimit-Reset"


def rate_limit(
    policy: RateLimitPolicy = DEFAULT_POLICY,
    key_prefix: str = "api",
):
    """Return a FastAPI dependency that enforces *policy* for the route.

    The identifier is the client IP address (suitable for both authenticated
    and unauthenticated endpoints). When ``rate_limit_enabled`` is ``False``
    in settings the dependency is a no-op.

    Rate-limit headers are attached to every response regardless of whether
    the limit was exceeded.

    Usage::

        @router.post("/ingest")
        async def ingest(
            _: None = Depends(rate_limit(INGEST_POLICY, key_prefix="ingest")),
        ):
            ...
    """

    async def _dependency(request: Request, response: Response) -> None:
        settings = get_settings()
        if not settings.rate_limit_enabled:
            return

        client_ip = request.client.host if request.client else "unknown"
        key = f"{key_prefix}:{client_ip}"

        limiter = get_rate_limiter()
        allowed, remaining, reset_at = await limiter.is_allowed(key, policy)

        response.headers[_HEADER_LIMIT] = str(policy.max_requests)
        response.headers[_HEADER_REMAINING] = str(remaining)
        response.headers[_HEADER_RESET] = str(reset_at)

        if not allowed:
            raise RateLimitError(
                f"Rate limit exceeded. Limit: {policy.max_requests} requests "
                f"per {policy.window_seconds}s. Resets at {reset_at}."
            )

    return _dependency
