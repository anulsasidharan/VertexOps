"""Integration tests for the Indexes API endpoints."""

import uuid
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

from fastapi.testclient import TestClient

from backend.api.dependencies import get_current_user
from backend.api.dependencies.auth import AuthContext
from backend.api.v1.indexes import get_index_service
from backend.core.exceptions import ForbiddenError, NotFoundError
from backend.main import app
from backend.repositories.index_repository import IndexRepository

_WS_ID = uuid.UUID("00000000-0000-0000-0000-000000000010")
_USER_ID = uuid.UUID("00000000-0000-0000-0000-000000000011")
_IDX_ID = uuid.UUID("00000000-0000-0000-0000-000000000012")
_NOW = datetime(2026, 4, 17, 12, 0, 0)


def _auth(workspace_id=_WS_ID):
    return AuthContext(
        user_id=_USER_ID, role="member", workspace_id=workspace_id, auth_type="jwt"
    )


def _make_idx(**kwargs):
    idx = MagicMock()
    idx.id = kwargs.get("id", _IDX_ID)
    idx.workspace_id = kwargs.get("workspace_id", _WS_ID)
    idx.name = kwargs.get("name", "My Index")
    idx.vector_backend = kwargs.get("vector_backend", "pinecone")
    idx.namespace = kwargs.get("namespace", None)
    idx.config_hash = kwargs.get("config_hash", None)
    idx.index_config = kwargs.get("index_config", None)
    idx.status = kwargs.get("status", "building")
    idx.created_at = _NOW
    idx.updated_at = _NOW
    return idx


def _make_repo(**overrides):
    repo = MagicMock(spec=IndexRepository)
    repo.add = AsyncMock(return_value=_make_idx())
    repo.list_by_workspace = AsyncMock(return_value=[_make_idx()])
    repo.get = AsyncMock(return_value=_make_idx())
    repo.session = MagicMock()
    repo.session.flush = AsyncMock()
    repo.session.refresh = AsyncMock()
    for k, v in overrides.items():
        setattr(repo, k, v)
    return repo


client = TestClient(app, raise_server_exceptions=False)


# ---------------------------------------------------------------------------
# POST /indexes
# ---------------------------------------------------------------------------


class TestCreateIndex:
    def setup_method(self):
        self._repo = _make_repo()
        app.dependency_overrides[get_current_user] = lambda: _auth()
        app.dependency_overrides[get_index_service] = lambda: self._repo

    def teardown_method(self):
        app.dependency_overrides.clear()

    def test_create_returns_201(self):
        resp = client.post("/api/v1/indexes", json={"name": "My Index"})
        assert resp.status_code == 201
        body = resp.json()
        assert body["id"] == str(_IDX_ID)
        assert body["status"] == "building"

    def test_create_response_shape(self):
        resp = client.post("/api/v1/indexes", json={"name": "x"})
        body = resp.json()
        for f in ("id", "workspace_id", "name", "status", "created_at"):
            assert f in body

    def test_create_unauthenticated_returns_401(self):
        app.dependency_overrides.clear()
        resp = client.post("/api/v1/indexes", json={"name": "x"})
        assert resp.status_code == 401

    def test_create_no_workspace_returns_403(self):
        app.dependency_overrides[get_current_user] = lambda: _auth(workspace_id=None)
        resp = client.post("/api/v1/indexes", json={"name": "x"})
        assert resp.status_code == 403


# ---------------------------------------------------------------------------
# GET /indexes
# ---------------------------------------------------------------------------


class TestListIndexes:
    def setup_method(self):
        self._repo = _make_repo()
        app.dependency_overrides[get_current_user] = lambda: _auth()
        app.dependency_overrides[get_index_service] = lambda: self._repo

    def teardown_method(self):
        app.dependency_overrides.clear()

    def test_list_returns_200(self):
        resp = client.get("/api/v1/indexes")
        assert resp.status_code == 200
        body = resp.json()
        assert "items" in body
        assert body["total"] == 1

    def test_list_unauthenticated_returns_401(self):
        app.dependency_overrides.clear()
        resp = client.get("/api/v1/indexes")
        assert resp.status_code == 401

    def test_list_empty(self):
        self._repo.list_by_workspace = AsyncMock(return_value=[])
        resp = client.get("/api/v1/indexes")
        assert resp.json()["total"] == 0


# ---------------------------------------------------------------------------
# GET /indexes/{id}
# ---------------------------------------------------------------------------


class TestGetIndex:
    def setup_method(self):
        self._repo = _make_repo()
        app.dependency_overrides[get_current_user] = lambda: _auth()
        app.dependency_overrides[get_index_service] = lambda: self._repo

    def teardown_method(self):
        app.dependency_overrides.clear()

    def test_get_returns_200(self):
        resp = client.get(f"/api/v1/indexes/{_IDX_ID}")
        assert resp.status_code == 200
        assert resp.json()["id"] == str(_IDX_ID)

    def test_get_not_found_returns_404(self):
        self._repo.get = AsyncMock(return_value=None)
        resp = client.get(f"/api/v1/indexes/{_IDX_ID}")
        assert resp.status_code == 404

    def test_get_wrong_workspace_returns_403(self):
        other_ws = uuid.uuid4()
        self._repo.get = AsyncMock(return_value=_make_idx(workspace_id=other_ws))
        resp = client.get(f"/api/v1/indexes/{_IDX_ID}")
        assert resp.status_code == 403


# ---------------------------------------------------------------------------
# POST /indexes/{id}/rebuild
# ---------------------------------------------------------------------------


class TestRebuildIndex:
    def setup_method(self):
        self._repo = _make_repo()
        app.dependency_overrides[get_current_user] = lambda: _auth()
        app.dependency_overrides[get_index_service] = lambda: self._repo

    def teardown_method(self):
        app.dependency_overrides.clear()

    def test_rebuild_returns_200(self):
        resp = client.post(f"/api/v1/indexes/{_IDX_ID}/rebuild")
        assert resp.status_code == 200

    def test_rebuild_sets_status_building(self):
        idx = _make_idx(status="ready")
        self._repo.get = AsyncMock(return_value=idx)
        client.post(f"/api/v1/indexes/{_IDX_ID}/rebuild")
        assert idx.status == "building"

    def test_rebuild_not_found_returns_404(self):
        self._repo.get = AsyncMock(return_value=None)
        resp = client.post(f"/api/v1/indexes/{_IDX_ID}/rebuild")
        assert resp.status_code == 404

    def test_rebuild_unauthenticated_returns_401(self):
        app.dependency_overrides.clear()
        resp = client.post(f"/api/v1/indexes/{_IDX_ID}/rebuild")
        assert resp.status_code == 401
