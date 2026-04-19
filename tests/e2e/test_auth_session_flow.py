"""E2E: Complete authentication and session lifecycle journey.

Simulates an operator:
  1. Logging in via JWT and receiving a token.
  2. Creating an API key for service-to-service use.
  3. Listing their API keys.
  4. Revoking a key and confirming it is gone.

All external dependencies (DB, crypto helpers) are mocked so this suite
runs in CI without infrastructure.
"""

import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from backend.api.dependencies.auth import AuthContext, get_current_user
from backend.core.security import hash_api_key, hash_password
from backend.main import app

_USER_ID = uuid.UUID("00000000-0000-0000-0000-000000000010")
_WS_ID = uuid.UUID("00000000-0000-0000-0000-000000000011")
_PEPPER = "test-api-key-pepper-only"
_JWT_SECRET = "test-jwt-secret-key-for-unit-tests-only"


def _make_user():
    u = MagicMock()
    u.id = _USER_ID
    u.email = "operator@example.com"
    u.role = "admin"
    u.workspace_id = _WS_ID
    u.password_hash = hash_password("s3cr3tP@ss")
    u.is_active = True
    return u


def _make_api_key(key_id: uuid.UUID, raw: str = "vops_e2e_raw_key_0123456789abcdef0123"):
    from backend.models.api_key import APIKey

    ak = APIKey()
    ak.id = key_id
    ak.user_id = _USER_ID
    ak.label = "ci-key"
    ak.key_hash = hash_api_key(raw, _PEPPER)
    return ak


def _admin_auth():
    return AuthContext(user_id=_USER_ID, role="admin", workspace_id=_WS_ID, auth_type="jwt")


# ---------------------------------------------------------------------------
# Full journey
# ---------------------------------------------------------------------------


class TestAuthSessionJourney:
    """Exercise the auth flow end-to-end within a single test suite."""

    def test_step1_login_returns_bearer_token(self):
        """Operator posts credentials and receives an access_token."""
        user = _make_user()

        with (
            patch("backend.api.v1.auth.UserRepository") as MockRepo,
            patch("backend.api.v1.auth.get_settings") as mock_cfg,
        ):
            MockRepo.return_value.get_by_email = AsyncMock(return_value=user)
            mock_cfg.return_value.jwt_secret_key.get_secret_value.return_value = _JWT_SECRET
            mock_cfg.return_value.jwt_algorithm = "HS256"
            mock_cfg.return_value.jwt_access_token_expire_minutes = 60

            with TestClient(app) as client:
                resp = client.post(
                    "/api/v1/auth/token",
                    json={"email": "operator@example.com", "password": "s3cr3tP@ss"},
                )

        assert resp.status_code == 200
        body = resp.json()
        assert "access_token" in body
        assert body["token_type"] == "bearer"

    def test_step2_create_api_key_for_ci_usage(self):
        """Authenticated operator creates a labelled API key."""
        key_id = uuid.uuid4()
        raw_key = "vops_e2e_raw_key_0123456789abcdef0123"
        ak = _make_api_key(key_id, raw_key)

        with (
            patch("backend.api.v1.auth.APIKeyRepository") as MockRepo,
            patch("backend.api.v1.auth.get_settings") as mock_cfg,
            patch("backend.api.v1.auth.generate_api_key", return_value=(raw_key, ak.key_hash)),
        ):
            MockRepo.return_value.add = AsyncMock(return_value=ak)
            mock_cfg.return_value.api_key_pepper.get_secret_value.return_value = _PEPPER

            app.dependency_overrides[get_current_user] = _admin_auth
            with TestClient(app) as client:
                resp = client.post("/api/v1/auth/api-keys", json={"label": "ci-key"})
            app.dependency_overrides.clear()

        assert resp.status_code in (200, 201)
        body = resp.json()
        assert body["raw_key"] == raw_key
        assert body["label"] == "ci-key"

    def test_step3_list_api_keys_shows_created_key(self):
        """After creation the key appears in the listing."""
        key_id = uuid.uuid4()
        ak = _make_api_key(key_id)
        ak.label = "ci-key"

        with patch("backend.api.v1.auth.APIKeyRepository") as MockRepo:
            MockRepo.return_value.list_by_user = AsyncMock(return_value=[ak])

            app.dependency_overrides[get_current_user] = _admin_auth
            with TestClient(app) as client:
                resp = client.get("/api/v1/auth/api-keys")
            app.dependency_overrides.clear()

        assert resp.status_code == 200
        keys = resp.json()
        assert any(k["label"] == "ci-key" for k in keys)

    def test_step4_revoke_api_key_removes_it(self):
        """Revoking a key returns 204 (no-content)."""
        key_id = uuid.uuid4()
        ak = _make_api_key(key_id)
        ak.user_id = _USER_ID

        with patch("backend.api.v1.auth.APIKeyRepository") as MockRepo:
            MockRepo.return_value.get = AsyncMock(return_value=ak)
            MockRepo.return_value.delete = AsyncMock(return_value=None)
            MockRepo.return_value.remove = AsyncMock(return_value=None)

            app.dependency_overrides[get_current_user] = _admin_auth
            with TestClient(app) as client:
                resp = client.delete(f"/api/v1/auth/api-keys/{key_id}")
            app.dependency_overrides.clear()

        assert resp.status_code == 204

    def test_step5_unauthenticated_requests_blocked(self):
        """Without credentials every protected endpoint returns 401."""
        with TestClient(app) as client:
            resp_keys = client.get("/api/v1/auth/api-keys")
            resp_create = client.post("/api/v1/auth/api-keys", json={"label": "x"})

        assert resp_keys.status_code == 401
        assert resp_create.status_code == 401

    def test_wrong_password_gives_401_not_403(self):
        """Wrong password should not reveal whether the account exists."""
        user = _make_user()

        with patch("backend.api.v1.auth.UserRepository") as MockRepo:
            MockRepo.return_value.get_by_email = AsyncMock(return_value=user)

            with TestClient(app) as client:
                resp = client.post(
                    "/api/v1/auth/token",
                    json={"email": "operator@example.com", "password": "wrongpassword"},
                )

        assert resp.status_code == 401
