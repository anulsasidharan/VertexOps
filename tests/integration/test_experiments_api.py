"""Integration tests for the Experiments API."""

import uuid
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi.testclient import TestClient

from backend.api.dependencies.auth import AuthContext, get_current_user
from backend.api.v1.experiments import get_experiment_service
from backend.core.exceptions import ForbiddenError, NotFoundError
from backend.main import app

_WS_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")
_EXP_ID = uuid.UUID("00000000-0000-0000-0000-000000000002")
_RUN_ID = uuid.UUID("00000000-0000-0000-0000-000000000003")
_NOW = datetime(2026, 4, 18, 12, 0, 0)


def _auth(workspace_id=_WS_ID):
    return AuthContext(user_id=uuid.uuid4(), role="member", workspace_id=workspace_id, auth_type="jwt")


def _no_ws_auth():
    return AuthContext(user_id=uuid.uuid4(), role="member", workspace_id=None, auth_type="jwt")


def _make_exp(**kwargs):
    exp = MagicMock()
    exp.id = kwargs.get("id", _EXP_ID)
    exp.workspace_id = kwargs.get("workspace_id", _WS_ID)
    exp.name = kwargs.get("name", "test-exp")
    exp.description = kwargs.get("description", None)
    exp.index_id = kwargs.get("index_id", None)
    exp.experiment_config = kwargs.get("experiment_config", {"top_k": 5})
    exp.config_hash = kwargs.get("config_hash", "a" * 64)
    exp.created_at = _NOW
    exp.updated_at = _NOW
    return exp


def _make_run(**kwargs):
    run = MagicMock()
    run.id = kwargs.get("id", _RUN_ID)
    run.experiment_id = kwargs.get("experiment_id", _EXP_ID)
    run.status = kwargs.get("status", "queued")
    run.started_at = None
    run.finished_at = None
    return run


# ---------------------------------------------------------------------------
# POST /experiments
# ---------------------------------------------------------------------------

def test_create_experiment_happy_path():
    mock_svc = MagicMock()
    mock_svc.create = AsyncMock(return_value=_make_exp())

    app.dependency_overrides[get_current_user] = _auth
    app.dependency_overrides[get_experiment_service] = lambda: mock_svc

    with TestClient(app) as client:
        resp = client.post("/api/v1/experiments", json={
            "name": "test-exp",
            "config": {"top_k": 5},
        })

    app.dependency_overrides.clear()
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "test-exp"
    assert data["config"] == {"top_k": 5}
    assert data.get("config_hash") == "a" * 64


def test_create_experiment_no_workspace_returns_403():
    mock_svc = MagicMock()
    app.dependency_overrides[get_current_user] = _no_ws_auth
    app.dependency_overrides[get_experiment_service] = lambda: mock_svc

    with TestClient(app) as client:
        resp = client.post("/api/v1/experiments", json={"name": "x"})

    app.dependency_overrides.clear()
    assert resp.status_code == 403


def test_create_experiment_missing_name_returns_422():
    app.dependency_overrides[get_current_user] = _auth
    app.dependency_overrides[get_experiment_service] = lambda: MagicMock()

    with TestClient(app) as client:
        resp = client.post("/api/v1/experiments", json={})

    app.dependency_overrides.clear()
    assert resp.status_code == 422


# ---------------------------------------------------------------------------
# GET /experiments
# ---------------------------------------------------------------------------

def test_list_experiments_returns_items():
    mock_svc = MagicMock()
    mock_svc.list = AsyncMock(return_value=[_make_exp(), _make_exp(id=uuid.uuid4(), name="exp2")])

    app.dependency_overrides[get_current_user] = _auth
    app.dependency_overrides[get_experiment_service] = lambda: mock_svc

    with TestClient(app) as client:
        resp = client.get("/api/v1/experiments")

    app.dependency_overrides.clear()
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 2
    assert len(data["items"]) == 2


def test_list_experiments_no_workspace_returns_empty():
    mock_svc = MagicMock()
    app.dependency_overrides[get_current_user] = _no_ws_auth
    app.dependency_overrides[get_experiment_service] = lambda: mock_svc

    with TestClient(app) as client:
        resp = client.get("/api/v1/experiments")

    app.dependency_overrides.clear()
    assert resp.status_code == 200
    assert resp.json()["total"] == 0


def test_list_experiments_requires_auth():
    with TestClient(app) as client:
        resp = client.get("/api/v1/experiments")
    assert resp.status_code == 401


# ---------------------------------------------------------------------------
# GET /experiments/{id}
# ---------------------------------------------------------------------------

def test_get_experiment_happy_path():
    mock_svc = MagicMock()
    mock_svc.get = AsyncMock(return_value=_make_exp())

    app.dependency_overrides[get_current_user] = _auth
    app.dependency_overrides[get_experiment_service] = lambda: mock_svc

    with TestClient(app) as client:
        resp = client.get(f"/api/v1/experiments/{_EXP_ID}")

    app.dependency_overrides.clear()
    assert resp.status_code == 200
    assert resp.json()["id"] == str(_EXP_ID)


def test_get_experiment_not_found_returns_404():
    mock_svc = MagicMock()
    mock_svc.get = AsyncMock(side_effect=NotFoundError("not found"))

    app.dependency_overrides[get_current_user] = _auth
    app.dependency_overrides[get_experiment_service] = lambda: mock_svc

    with TestClient(app) as client:
        resp = client.get(f"/api/v1/experiments/{_EXP_ID}")

    app.dependency_overrides.clear()
    assert resp.status_code == 404


def test_get_experiment_wrong_workspace_returns_403():
    mock_svc = MagicMock()
    mock_svc.get = AsyncMock(side_effect=ForbiddenError("wrong workspace"))

    app.dependency_overrides[get_current_user] = _auth
    app.dependency_overrides[get_experiment_service] = lambda: mock_svc

    with TestClient(app) as client:
        resp = client.get(f"/api/v1/experiments/{_EXP_ID}")

    app.dependency_overrides.clear()
    assert resp.status_code == 403


# ---------------------------------------------------------------------------
# POST /experiments/{id}/run
# ---------------------------------------------------------------------------

def test_kickoff_run_happy_path():
    mock_svc = MagicMock()
    mock_svc.kickoff_run = AsyncMock(return_value=_make_run())

    app.dependency_overrides[get_current_user] = _auth
    app.dependency_overrides[get_experiment_service] = lambda: mock_svc

    with TestClient(app) as client:
        resp = client.post(f"/api/v1/experiments/{_EXP_ID}/run", json={})

    app.dependency_overrides.clear()
    assert resp.status_code == 201
    data = resp.json()
    assert data["status"] == "queued"
    assert data["experiment_id"] == str(_EXP_ID)


def test_kickoff_run_not_found_returns_404():
    mock_svc = MagicMock()
    mock_svc.kickoff_run = AsyncMock(side_effect=NotFoundError("not found"))

    app.dependency_overrides[get_current_user] = _auth
    app.dependency_overrides[get_experiment_service] = lambda: mock_svc

    with TestClient(app) as client:
        resp = client.post(f"/api/v1/experiments/{_EXP_ID}/run", json={})

    app.dependency_overrides.clear()
    assert resp.status_code == 404


def test_kickoff_run_with_custom_config():
    mock_svc = MagicMock()
    mock_svc.kickoff_run = AsyncMock(return_value=_make_run())

    app.dependency_overrides[get_current_user] = _auth
    app.dependency_overrides[get_experiment_service] = lambda: mock_svc

    with TestClient(app) as client:
        resp = client.post(f"/api/v1/experiments/{_EXP_ID}/run", json={
            "run_config": {"top_k": 10, "temperature": 0.3}
        })

    app.dependency_overrides.clear()
    assert resp.status_code == 201
    _, kwargs = mock_svc.kickoff_run.call_args
    assert kwargs["run_config"] == {"top_k": 10, "temperature": 0.3}
