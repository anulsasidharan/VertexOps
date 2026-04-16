"""Smoke test — app boots and health endpoint responds."""

from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)


def test_health():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_ready():
    response = client.get("/api/v1/ready")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
