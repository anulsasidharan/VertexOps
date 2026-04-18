"""Redis-backed rate limiter with fixed-window counter and fail-open fallback."""

import logging
import time
from typing import NamedTuple, Optional, Tuple

import redis.asyncio as aioredis

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Policy definitions
# ---------------------------------------------------------------------------


class RateLimitPolicy(NamedTuple):
    """Configures a fixed-window rate limit."""

    max_requests: int
    window_seconds: int


# Preset policies — callers may define their own.
DEFAULT_POLICY = RateLimitPolicy(max_requests=100, window_seconds=60)
STRICT_POLICY = RateLimitPolicy(max_requests=20, window_seconds=60)
INGEST_POLICY = RateLimitPolicy(max_requests=10, window_seconds=60)
QUERY_POLICY = RateLimitPolicy(max_requests=50, window_seconds=60)


# ---------------------------------------------------------------------------
# Rate limiter
# ---------------------------------------------------------------------------


class RateLimiter:
    """Fixed-window rate limiter backed by Redis.

    - Uses ``INCR`` + ``EXPIRE`` inside a pipeline for atomic counting.
    - Fails open (allows request) when Redis is unreachable so that a Redis
      outage does not take down the API.
    """

    def __init__(self, redis_url: str) -> None:
        self._redis_url = redis_url
        self._client: Optional[aioredis.Redis] = None

    def _get_client(self) -> aioredis.Redis:
        if self._client is None:
            self._client = aioredis.from_url(
                self._redis_url,
                decode_responses=True,
                socket_connect_timeout=1,
                socket_timeout=1,
            )
        return self._client

    async def is_allowed(
        self, key: str, policy: RateLimitPolicy
    ) -> Tuple[bool, int, int]:
        """Check whether *key* is within *policy* for the current window.

        Returns ``(allowed, remaining, reset_at_unix)``.
        Fails open — returns ``(True, max_requests, 0)`` on any Redis error.
        """
        client = self._get_client()
        window_slot = int(time.time()) // policy.window_seconds
        redis_key = f"rl:{key}:{window_slot}"
        reset_at = (window_slot + 1) * policy.window_seconds

        try:
            pipe = client.pipeline()
            pipe.incr(redis_key)
            pipe.expire(redis_key, policy.window_seconds)
            results = await pipe.execute()
            count: int = results[0]
            remaining = max(0, policy.max_requests - count)
            allowed = count <= policy.max_requests
            return allowed, remaining, reset_at
        except Exception:
            logger.warning("rate limiter: Redis unavailable — failing open")
            return True, policy.max_requests, 0

    async def check_connectivity(self) -> bool:
        """Ping Redis; used by the readiness probe."""
        client = self._get_client()
        try:
            await client.ping()
            return True
        except Exception:
            return False


# ---------------------------------------------------------------------------
# Singleton
# ---------------------------------------------------------------------------

_limiter: Optional[RateLimiter] = None


def get_rate_limiter() -> RateLimiter:
    """Return the process-wide RateLimiter, creating it on first call."""
    global _limiter
    if _limiter is None:
        from backend.core.config import get_settings

        _limiter = RateLimiter(redis_url=get_settings().redis_url)
    return _limiter


async def check_redis_connectivity() -> bool:
    """Convenience wrapper used by the readiness endpoint."""
    return await get_rate_limiter().check_connectivity()
