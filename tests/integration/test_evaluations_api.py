"""Integration tests for the Evaluations API."""

import uuid
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi.testclient import TestClient

from backend.api.dependencies.auth import AuthContext, get_current_user
from backend.api.v1.evaluations import get_evaluation_lifecycle_service
from backend.core.db import get_db
from backend.core.exceptions import NotFoundError
from backend.main import app

_WS_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")
_EXP_ID = uuid.UUID("00000000-0000-0000-0000-000000000002")
_RUN_ID = uuid.UUID("00000000-0000-0000-0000-000000000003")
_NOW = datetime(2026, 4, 18, 12, 0, 0)


def _auth(workspace_id=_WS_ID):
    return AuthContext(
        user_id=uuid.uuid4(), role="member", workspace_id=workspace_id, auth_type="jwt"
    )


def _no_ws_auth():
    return AuthContext(
        user_id=uuid.uuid4(), role="member", workspace_id=None, auth_type="jwt"
    )


def _make_run(**kwargs):
    run = MagicMock()
    run.id = kwargs.get("id", _RUN_ID)
    run.experiment_id = kwargs.get("experiment_id", _EXP_ID)
    run.status = kwargs.get("status", "queued")
    run.started_at = kwargs.get("started_at", None)
    run.finished_at = kwargs.get("finished_at", None)
    run.artifact_uri = kwargs.get("artifact_uri", None)
    run.run_logs = kwargs.get("run_logs", {})
    return run


# ---------------------------------------------------------------------------
# POST /evaluations
# ---------------------------------------------------------------------------


def test_create_evaluation_happy_path(monkeypatch):
    captured = []

    def fake_enqueue(rid: uuid.UUID) -> None:
        captured.append(rid)

    monkeypatch.setattr(
        "backend.api.v1.evaluations._enqueue_evaluation_worker", fake_enqueue
    )

    mock_lifecycle = MagicMock()
    mock_lifecycle.start_evaluation = AsyncMock(return_value=_make_run())

    mock_session = MagicMock()
    mock_session.commit = AsyncMock()

    app.dependency_overrides[get_current_user] = _auth
    app.dependency_overrides[get_evaluation_lifecycle_service] = lambda: mock_lifecycle
    app.dependency_overrides[get_db] = lambda: mock_session

    with TestClient(app) as client:
        resp = client.post(
            "/api/v1/evaluations",
            json={
                "experiment_id": str(_EXP_ID),
                "cases": [
                    {
                        "question": "What is X?",
                        "predicted": "X is a test value.",
                        "ground_truth": "X is a test value.",
                    }
                ],
            },
        )

    app.dependency_overrides.clear()
    assert resp.status_code == 201
    data = resp.json()
    assert data["id"] == str(_RUN_ID)
    assert data["status"] == "queued"
    mock_lifecycle.start_evaluation.assert_awaited_once()
    mock_session.commit.assert_awaited_once()
    assert captured == [_RUN_ID]


def test_create_evaluation_no_workspace_returns_403():
    mock_lifecycle = MagicMock()
    mock_session = MagicMock()
    app.dependency_overrides[get_current_user] = _no_ws_auth
    app.dependency_overrides[get_evaluation_lifecycle_service] = lambda: mock_lifecycle
    app.dependency_overrides[get_db] = lambda: mock_session

    with TestClient(app) as client:
        resp = client.post(
            "/api/v1/evaluations",
            json={
                "experiment_id": str(_EXP_ID),
                "cases": [{"question": "Q?", "predicted": "A"}],
            },
        )

    app.dependency_overrides.clear()
    assert resp.status_code == 403


def test_create_evaluation_requires_cases():
    mock_lifecycle = MagicMock()
    mock_session = MagicMock()
    app.dependency_overrides[get_current_user] = _auth
    app.dependency_overrides[get_evaluation_lifecycle_service] = lambda: mock_lifecycle
    app.dependency_overrides[get_db] = lambda: mock_session

    with TestClient(app) as client:
        resp = client.post(
            "/api/v1/evaluations",
            json={"experiment_id": str(_EXP_ID), "cases": []},
        )

    app.dependency_overrides.clear()
    assert resp.status_code == 422


# ---------------------------------------------------------------------------
# GET /evaluations/{id}
# ---------------------------------------------------------------------------


def test_get_evaluation_detail():
    mock_lifecycle = MagicMock()
    mock_lifecycle.get_detail = AsyncMock(
        return_value={
            "id": _RUN_ID,
            "experiment_id": _EXP_ID,
            "status": "completed",
            "started_at": _NOW,
            "finished_at": _NOW,
            "artifact_uri": "file:///tmp/report.json",
            "metrics": {"case_count": 1},
        }
    )

    app.dependency_overrides[get_current_user] = _auth
    app.dependency_overrides[get_evaluation_lifecycle_service] = lambda: mock_lifecycle

    with TestClient(app) as client:
        resp = client.get(f"/api/v1/evaluations/{_RUN_ID}")

    app.dependency_overrides.clear()
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "completed"
    assert body["metrics"]["case_count"] == 1


def test_get_evaluation_not_found():
    mock_lifecycle = MagicMock()
    mock_lifecycle.get_detail = AsyncMock(side_effect=NotFoundError("missing"))

    app.dependency_overrides[get_current_user] = _auth
    app.dependency_overrides[get_evaluation_lifecycle_service] = lambda: mock_lifecycle

    with TestClient(app) as client:
        resp = client.get(f"/api/v1/evaluations/{_RUN_ID}")

    app.dependency_overrides.clear()
    assert resp.status_code == 404


# ---------------------------------------------------------------------------
# GET /evaluations/{id}/report
# ---------------------------------------------------------------------------


def test_get_evaluation_report_json(monkeypatch):
    from backend.api.v1 import evaluations as eval_module

    mock_lifecycle = MagicMock()
    run = _make_run(
        run_logs={"artifact_key": f"artifacts/{_RUN_ID}/report.json"},
    )
    mock_lifecycle.get_run_for_workspace = AsyncMock(return_value=run)

    mock_storage = MagicMock()
    mock_storage.get = AsyncMock(return_value=b'{"ok": true}')

    monkeypatch.setattr(eval_module, "get_storage_backend", lambda: mock_storage)

    app.dependency_overrides[get_current_user] = _auth
    app.dependency_overrides[get_evaluation_lifecycle_service] = lambda: mock_lifecycle

    with TestClient(app) as client:
        resp = client.get(f"/api/v1/evaluations/{_RUN_ID}/report?format=json")

    app.dependency_overrides.clear()
    assert resp.status_code == 200
    assert resp.headers["content-type"].startswith("application/json")
    assert resp.content == b'{"ok": true}'


def test_get_evaluation_report_not_ready():
    from backend.api.v1 import evaluations as eval_module
    from unittest.mock import patch

    mock_lifecycle = MagicMock()
    run = _make_run(run_logs={})
    mock_lifecycle.get_run_for_workspace = AsyncMock(return_value=run)

    mock_storage = MagicMock()
    mock_storage.get = AsyncMock(side_effect=NotFoundError("no key"))

    app.dependency_overrides[get_current_user] = _auth
    app.dependency_overrides[get_evaluation_lifecycle_service] = lambda: mock_lifecycle

    with patch.object(eval_module, "get_storage_backend", return_value=mock_storage):
        with TestClient(app) as client:
            resp = client.get(f"/api/v1/evaluations/{_RUN_ID}/report")

    app.dependency_overrides.clear()
    assert resp.status_code == 404
