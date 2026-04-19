"""Unit tests for the Prometheus /metrics endpoint."""

from unittest.mock import patch

from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)


class TestMetricsEndpointDisabled:
    def test_returns_404_when_metrics_disabled(self):
        """Default: METRICS_ENABLED=false → 404."""
        with patch("backend.api.v1.metrics.get_settings") as mock_cfg:
            mock_cfg.return_value.metrics_enabled = False
            resp = client.get("/api/v1/metrics")
        assert resp.status_code == 404

    def test_404_body_is_json(self):
        with patch("backend.api.v1.metrics.get_settings") as mock_cfg:
            mock_cfg.return_value.metrics_enabled = False
            resp = client.get("/api/v1/metrics")
        assert resp.headers["content-type"].startswith("application/json")


class TestMetricsEndpointEnabled:
    def test_returns_200_when_enabled(self):
        with patch("backend.api.v1.metrics.get_settings") as mock_cfg:
            mock_cfg.return_value.metrics_enabled = True
            resp = client.get("/api/v1/metrics")
        assert resp.status_code == 200

    def test_content_type_is_prometheus_text(self):
        with patch("backend.api.v1.metrics.get_settings") as mock_cfg:
            mock_cfg.return_value.metrics_enabled = True
            resp = client.get("/api/v1/metrics")
        assert "text/plain" in resp.headers["content-type"]

    def test_body_contains_vertexops_metrics(self):
        with patch("backend.api.v1.metrics.get_settings") as mock_cfg:
            mock_cfg.return_value.metrics_enabled = True
            resp = client.get("/api/v1/metrics")
        assert b"vertexops_" in resp.content

    def test_endpoint_excluded_from_openapi_schema(self):
        """Metrics must not appear in the public Swagger schema."""
        resp = client.get("/openapi.json")
        assert resp.status_code == 200
        paths = resp.json().get("paths", {})
        assert "/api/v1/metrics" not in paths
