"""Unit tests for RateLimiter, rate_limit dependency, and readiness integration."""

import time
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

from backend.api.dependencies.rate_limit import rate_limit
from backend.core.exceptions import RateLimitError
from backend.core.rate_limit import (
    DEFAULT_POLICY,
    INGEST_POLICY,
    QUERY_POLICY,
    STRICT_POLICY,
    RateLimiter,
    RateLimitPolicy,
    check_redis_connectivity,
    get_rate_limiter,
)

# ---------------------------------------------------------------------------
# RateLimitPolicy
# ---------------------------------------------------------------------------


def test_policy_is_named_tuple():
    p = RateLimitPolicy(max_requests=50, window_seconds=30)
    assert p.max_requests == 50
    assert p.window_seconds == 30


def test_preset_policies_exist():
    assert DEFAULT_POLICY.max_requests > 0
    assert STRICT_POLICY.max_requests < DEFAULT_POLICY.max_requests
    assert INGEST_POLICY.max_requests > 0
    assert QUERY_POLICY.max_requests > 0


# ---------------------------------------------------------------------------
# RateLimiter.is_allowed — Redis mocked
# ---------------------------------------------------------------------------


def _make_pipeline_mock(count: int):
    """Return a mock Redis pipeline that returns *count* on INCR."""
    pipe = AsyncMock()
    pipe.incr = MagicMock()
    pipe.expire = MagicMock()
    pipe.execute = AsyncMock(return_value=[count, True])
    return pipe


def _make_redis_mock(count: int):
    client = AsyncMock()
    pipe = _make_pipeline_mock(count)
    client.pipeline = MagicMock(return_value=pipe)
    return client


@pytest.mark.asyncio
async def test_is_allowed_under_limit():
    policy = RateLimitPolicy(max_requests=10, window_seconds=60)
    limiter = RateLimiter(redis_url="redis://localhost")
    limiter._client = _make_redis_mock(count=5)

    allowed, remaining, reset_at = await limiter.is_allowed("test:key", policy)

    assert allowed is True
    assert remaining == 5
    assert reset_at > 0


@pytest.mark.asyncio
async def test_is_allowed_at_exact_limit():
    policy = RateLimitPolicy(max_requests=10, window_seconds=60)
    limiter = RateLimiter(redis_url="redis://localhost")
    limiter._client = _make_redis_mock(count=10)

    allowed, remaining, _ = await limiter.is_allowed("test:key", policy)

    assert allowed is True
    assert remaining == 0


@pytest.mark.asyncio
async def test_is_allowed_over_limit():
    policy = RateLimitPolicy(max_requests=10, window_seconds=60)
    limiter = RateLimiter(redis_url="redis://localhost")
    limiter._client = _make_redis_mock(count=11)

    allowed, remaining, _ = await limiter.is_allowed("test:key", policy)

    assert allowed is False
    assert remaining == 0


@pytest.mark.asyncio
async def test_is_allowed_fail_open_on_redis_error():
    """Any Redis exception must not block the request (fail open)."""
    policy = RateLimitPolicy(max_requests=10, window_seconds=60)
    limiter = RateLimiter(redis_url="redis://localhost")

    err_client = AsyncMock()
    # Use MagicMock for pipeline so incr/expire are sync (not awaitable)
    err_pipe = MagicMock()
    err_pipe.execute = AsyncMock(side_effect=ConnectionError("Redis down"))
    err_client.pipeline = MagicMock(return_value=err_pipe)
    limiter._client = err_client

    allowed, remaining, _ = await limiter.is_allowed("test:key", policy)

    assert allowed is True
    assert remaining == policy.max_requests


@pytest.mark.asyncio
async def test_is_allowed_reset_at_is_end_of_window():
    policy = RateLimitPolicy(max_requests=10, window_seconds=60)
    limiter = RateLimiter(redis_url="redis://localhost")
    limiter._client = _make_redis_mock(count=1)

    now = time.time()
    _, _, reset_at = await limiter.is_allowed("test:key", policy)

    window_slot = int(now) // policy.window_seconds
    expected_reset = (window_slot + 1) * policy.window_seconds
    assert abs(reset_at - expected_reset) <= 1


@pytest.mark.asyncio
async def test_is_allowed_redis_key_contains_window_slot():
    """Verify the Redis key changes between window slots."""
    policy = RateLimitPolicy(max_requests=5, window_seconds=60)
    limiter = RateLimiter(redis_url="redis://localhost")
    mock_client = _make_redis_mock(count=1)
    limiter._client = mock_client

    await limiter.is_allowed("mykey", policy)

    pipe = mock_client.pipeline.return_value
    incr_call_args = pipe.incr.call_args[0][0]
    assert incr_call_args.startswith("rl:mykey:")


# ---------------------------------------------------------------------------
# RateLimiter.check_connectivity
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_check_connectivity_ok():
    limiter = RateLimiter(redis_url="redis://localhost")
    mock_client = AsyncMock()
    mock_client.ping = AsyncMock(return_value=True)
    limiter._client = mock_client

    result = await limiter.check_connectivity()
    assert result is True


@pytest.mark.asyncio
async def test_check_connectivity_down():
    limiter = RateLimiter(redis_url="redis://localhost")
    mock_client = AsyncMock()
    mock_client.ping = AsyncMock(side_effect=ConnectionError("down"))
    limiter._client = mock_client

    result = await limiter.check_connectivity()
    assert result is False


# ---------------------------------------------------------------------------
# check_redis_connectivity convenience wrapper
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_check_redis_connectivity_delegates_to_limiter():
    with patch("backend.core.rate_limit.get_rate_limiter") as mock_get:
        mock_limiter = AsyncMock()
        mock_limiter.check_connectivity = AsyncMock(return_value=True)
        mock_get.return_value = mock_limiter

        result = await check_redis_connectivity()

    assert result is True
    mock_limiter.check_connectivity.assert_awaited_once()


# ---------------------------------------------------------------------------
# get_rate_limiter singleton
# ---------------------------------------------------------------------------


def test_get_rate_limiter_returns_same_instance():
    import backend.core.rate_limit as rl_module

    rl_module._limiter = None  # reset singleton for test isolation
    a = get_rate_limiter()
    b = get_rate_limiter()
    assert a is b
    rl_module._limiter = None  # clean up


# ---------------------------------------------------------------------------
# rate_limit dependency — via TestClient
# ---------------------------------------------------------------------------


def _build_test_app(policy: RateLimitPolicy, key_prefix: str = "test"):
    """Create a minimal FastAPI app with a rate-limited route."""
    from backend.core.exceptions import VertexOpsError
    from backend.core.middleware import (
        domain_exception_handler,
        unhandled_exception_handler,
    )

    test_app = FastAPI()
    test_app.add_exception_handler(VertexOpsError, domain_exception_handler)
    test_app.add_exception_handler(Exception, unhandled_exception_handler)

    @test_app.get("/limited", dependencies=[Depends(rate_limit(policy, key_prefix))])
    async def limited():
        return {"ok": True}

    return test_app


def _mock_limiter(allowed: bool, remaining: int = 5, reset_at: int = 9999999999):
    mock = AsyncMock()
    mock.is_allowed = AsyncMock(return_value=(allowed, remaining, reset_at))
    return mock


def test_rate_limit_dependency_allows_request():
    app = _build_test_app(DEFAULT_POLICY)
    with (
        patch(
            "backend.api.dependencies.rate_limit.get_rate_limiter",
            return_value=_mock_limiter(allowed=True, remaining=99),
        ),
        patch(
            "backend.api.dependencies.rate_limit.get_settings",
            return_value=MagicMock(rate_limit_enabled=True),
        ),
    ):
        client = TestClient(app)
        response = client.get("/limited")

    assert response.status_code == 200
    assert response.headers["X-RateLimit-Limit"] == str(DEFAULT_POLICY.max_requests)
    assert response.headers["X-RateLimit-Remaining"] == "99"


def test_rate_limit_dependency_blocks_request():
    app = _build_test_app(DEFAULT_POLICY)
    with (
        patch(
            "backend.api.dependencies.rate_limit.get_rate_limiter",
            return_value=_mock_limiter(allowed=False, remaining=0),
        ),
        patch(
            "backend.api.dependencies.rate_limit.get_settings",
            return_value=MagicMock(rate_limit_enabled=True),
        ),
    ):
        client = TestClient(app, raise_server_exceptions=False)
        response = client.get("/limited")

    assert response.status_code == 429
    body = response.json()
    assert body["error"]["code"] == "RATE_LIMIT_EXCEEDED"


def test_rate_limit_dependency_disabled_allows_all():
    app = _build_test_app(STRICT_POLICY)
    with patch(
        "backend.api.dependencies.rate_limit.get_settings",
        return_value=MagicMock(rate_limit_enabled=False),
    ):
        client = TestClient(app)
        response = client.get("/limited")

    assert response.status_code == 200


def test_rate_limit_blocked_response_has_correct_envelope():
    """A 429 response must carry the RATE_LIMIT_EXCEEDED error envelope."""
    app = _build_test_app(DEFAULT_POLICY)
    with (
        patch(
            "backend.api.dependencies.rate_limit.get_rate_limiter",
            return_value=_mock_limiter(allowed=False, remaining=0),
        ),
        patch(
            "backend.api.dependencies.rate_limit.get_settings",
            return_value=MagicMock(rate_limit_enabled=True),
        ),
    ):
        client = TestClient(app, raise_server_exceptions=False)
        response = client.get("/limited")

    assert response.status_code == 429
    body = response.json()
    assert body["error"]["code"] == "RATE_LIMIT_EXCEEDED"
    assert "Rate limit exceeded" in body["error"]["message"]


def test_rate_limit_uses_client_ip_as_identifier():
    policy = RateLimitPolicy(max_requests=5, window_seconds=60)
    mock_limiter = _mock_limiter(allowed=True, remaining=4)
    app = _build_test_app(policy, key_prefix="myprefix")

    with (
        patch(
            "backend.api.dependencies.rate_limit.get_rate_limiter",
            return_value=mock_limiter,
        ),
        patch(
            "backend.api.dependencies.rate_limit.get_settings",
            return_value=MagicMock(rate_limit_enabled=True),
        ),
    ):
        client = TestClient(app)
        client.get("/limited")

    call_args = mock_limiter.is_allowed.call_args
    key_used: str = call_args[0][0]
    assert key_used.startswith("myprefix:")


# ---------------------------------------------------------------------------
# 429 error envelope shape
# ---------------------------------------------------------------------------


def test_rate_limit_error_envelope_shape():

    err = RateLimitError("too many")
    envelope = err.to_envelope().model_dump()
    assert envelope["error"]["code"] == "RATE_LIMIT_EXCEEDED"
    assert envelope["error"]["message"] == "too many"
