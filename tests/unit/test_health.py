"""Smoke test — app boots and health/readiness endpoints respond."""

from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)


def test_health():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_ready_all_ok():
    with patch("backend.api.v1.health.check_db_connectivity", new=AsyncMock(return_value=True)):
        response = client.get("/api/v1/ready")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["checks"]["database"] == "ok"


def test_ready_db_down():
    with patch("backend.api.v1.health.check_db_connectivity", new=AsyncMock(return_value=False)):
        response = client.get("/api/v1/ready")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "degraded"
    assert body["checks"]["database"] == "unreachable"
