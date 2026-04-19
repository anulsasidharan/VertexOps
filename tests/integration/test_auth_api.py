"""Integration tests for the Auth API endpoints (JWT login, API key management)."""

import uuid
from unittest.mock import AsyncMock, MagicMock, patch

from fastapi.testclient import TestClient

from backend.api.dependencies.auth import AuthContext, get_current_user
from backend.core.security import hash_api_key, hash_password
from backend.main import app

_USER_ID = uuid.UUID("00000000-0000-0000-0000-000000000099")
_WS_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")
_PEPPER = "test-api-key-pepper-only"


def _admin_auth():
    return AuthContext(user_id=_USER_ID, role="admin", workspace_id=_WS_ID, auth_type="jwt")


def _member_auth():
    return AuthContext(user_id=_USER_ID, role="member", workspace_id=_WS_ID, auth_type="jwt")


def _make_user(role="member"):
    u = MagicMock()
    u.id = _USER_ID
    u.email = "test@example.com"
    u.role = role
    u.workspace_id = _WS_ID
    u.password_hash = hash_password("correct-password")
    u.is_active = True
    return u


def _make_api_key_obj(raw="vops_testrawkey123456789012345678901234"):
    from backend.models.api_key import APIKey

    ak = APIKey()
    ak.id = uuid.uuid4()
    ak.user_id = _USER_ID
    ak.label = "my-key"
    ak.key_hash = hash_api_key(raw, _PEPPER)
    return ak


# ---------------------------------------------------------------------------
# POST /auth/token — JWT login
# ---------------------------------------------------------------------------


class TestJwtLogin:
    def test_login_success(self):
        """Valid credentials return access_token."""
        user = _make_user()

        with (
            patch("backend.api.v1.auth.UserRepository") as MockRepo,
            patch("backend.api.v1.auth.get_settings") as mock_settings,
        ):
            MockRepo.return_value.get_by_email = AsyncMock(return_value=user)
            mock_settings.return_value.jwt_secret_key.get_secret_value.return_value = (
                "test-jwt-secret-key-for-unit-tests-only"
            )
            mock_settings.return_value.jwt_algorithm = "HS256"
            mock_settings.return_value.jwt_access_token_expire_minutes = 60

            with TestClient(app) as client:
                resp = client.post(
                    "/api/v1/auth/token",
                    json={"email": "test@example.com", "password": "correct-password"},
                )

        assert resp.status_code == 200
        body = resp.json()
        assert "access_token" in body
        assert body["token_type"] == "bearer"

    def test_login_wrong_password_returns_401(self):
        """Wrong password returns 401."""
        user = _make_user()

        with patch("backend.api.v1.auth.UserRepository") as MockRepo:
            MockRepo.return_value.get_by_email = AsyncMock(return_value=user)

            with TestClient(app) as client:
                resp = client.post(
                    "/api/v1/auth/token",
                    json={"email": "test@example.com", "password": "wrong-password"},
                )

        assert resp.status_code == 401

    def test_login_unknown_user_returns_401(self):
        """Unknown email returns 401 (no user enumeration)."""
        with patch("backend.api.v1.auth.UserRepository") as MockRepo:
            MockRepo.return_value.get_by_email = AsyncMock(return_value=None)

            with TestClient(app) as client:
                resp = client.post(
                    "/api/v1/auth/token",
                    json={"email": "nobody@example.com", "password": "any"},
                )

        assert resp.status_code == 401

    def test_login_missing_fields_returns_422(self):
        """Missing required fields return 422."""
        with TestClient(app) as client:
            resp = client.post("/api/v1/auth/token", json={"email": "test@example.com"})
        assert resp.status_code == 422


# ---------------------------------------------------------------------------
# POST /auth/api-keys — create API key
# ---------------------------------------------------------------------------


class TestApiKeyCreate:
    def test_create_api_key_success(self):
        """Authenticated user can create an API key."""
        ak = _make_api_key_obj()
        raw_key = "vops_returned_raw_key"

        with (
            patch("backend.api.v1.auth.APIKeyRepository") as MockRepo,
            patch("backend.api.v1.auth.get_settings") as mock_settings,
            patch("backend.api.v1.auth.generate_api_key", return_value=(raw_key, ak.key_hash)),
        ):
            MockRepo.return_value.add = AsyncMock(return_value=ak)
            mock_settings.return_value.api_key_pepper.get_secret_value.return_value = _PEPPER

            app.dependency_overrides[get_current_user] = _member_auth
            with TestClient(app) as client:
                resp = client.post(
                    "/api/v1/auth/api-keys",
                    json={"label": "my-key"},
                )
            app.dependency_overrides.clear()

        assert resp.status_code in (200, 201)
        body = resp.json()
        assert body["raw_key"] == raw_key
        assert body["label"] == "my-key"

    def test_create_api_key_unauthenticated_returns_401(self):
        with TestClient(app) as client:
            resp = client.post("/api/v1/auth/api-keys", json={"label": "x"})
        assert resp.status_code == 401


# ---------------------------------------------------------------------------
# GET /auth/api-keys — list keys
# ---------------------------------------------------------------------------


class TestApiKeyList:
    def test_list_api_keys(self):
        ak = _make_api_key_obj()
        ak.label = "listed-key"

        with patch("backend.api.v1.auth.APIKeyRepository") as MockRepo:
            MockRepo.return_value.list_by_user = AsyncMock(return_value=[ak])

            app.dependency_overrides[get_current_user] = _member_auth
            with TestClient(app) as client:
                resp = client.get("/api/v1/auth/api-keys")
            app.dependency_overrides.clear()

        assert resp.status_code == 200
        body = resp.json()
        assert isinstance(body, list)
        assert body[0]["label"] == "listed-key"

    def test_list_api_keys_unauthenticated(self):
        with TestClient(app) as client:
            resp = client.get("/api/v1/auth/api-keys")
        assert resp.status_code == 401


# ---------------------------------------------------------------------------
# DELETE /auth/api-keys/{key_id} — revoke
# ---------------------------------------------------------------------------


class TestApiKeyRevoke:
    def test_revoke_api_key_success(self):
        key_id = uuid.uuid4()
        ak = _make_api_key_obj()
        ak.id = key_id
        ak.user_id = _USER_ID

        with patch("backend.api.v1.auth.APIKeyRepository") as MockRepo:
            MockRepo.return_value.get = AsyncMock(return_value=ak)
            MockRepo.return_value.delete = AsyncMock(return_value=None)

            app.dependency_overrides[get_current_user] = _member_auth
            with TestClient(app) as client:
                resp = client.delete(f"/api/v1/auth/api-keys/{key_id}")
            app.dependency_overrides.clear()

        assert resp.status_code == 204

    def test_revoke_another_users_key_returns_403(self):
        key_id = uuid.uuid4()
        ak = _make_api_key_obj()
        ak.id = key_id
        ak.user_id = uuid.uuid4()  # different user

        with patch("backend.api.v1.auth.APIKeyRepository") as MockRepo:
            MockRepo.return_value.get = AsyncMock(return_value=ak)

            app.dependency_overrides[get_current_user] = _member_auth
            with TestClient(app) as client:
                resp = client.delete(f"/api/v1/auth/api-keys/{key_id}")
            app.dependency_overrides.clear()

        assert resp.status_code in (403, 404)

    def test_revoke_nonexistent_key_returns_404(self):
        with patch("backend.api.v1.auth.APIKeyRepository") as MockRepo:
            MockRepo.return_value.get = AsyncMock(return_value=None)

            app.dependency_overrides[get_current_user] = _member_auth
            with TestClient(app) as client:
                resp = client.delete(f"/api/v1/auth/api-keys/{uuid.uuid4()}")
            app.dependency_overrides.clear()

        assert resp.status_code == 404
