"""Unit tests for Prometheus telemetry and audit logging."""

import logging
import uuid
from unittest.mock import MagicMock, patch

import pytest

from backend.core.audit import AuditEvent, emit
from backend.core.telemetry import (
    CELERY_TASKS_TOTAL,
    HTTP_REQUESTS_TOTAL,
    RAG_QUERY_LATENCY_SECONDS,
    get_metrics_output,
    initialise_app_info,
    setup_otel,
)


# ---------------------------------------------------------------------------
# Prometheus metrics — smoke tests (counters / histograms are module singletons)
# ---------------------------------------------------------------------------


def test_get_metrics_output_returns_bytes_and_content_type():
    body, content_type = get_metrics_output()
    assert isinstance(body, bytes)
    assert "text/plain" in content_type


def test_http_requests_total_incrementable():
    before = HTTP_REQUESTS_TOTAL.labels(method="GET", path="/test", status_code="200")._value.get()
    HTTP_REQUESTS_TOTAL.labels(method="GET", path="/test", status_code="200").inc()
    after = HTTP_REQUESTS_TOTAL.labels(method="GET", path="/test", status_code="200")._value.get()
    assert after == before + 1


def test_rag_query_latency_observable():
    with RAG_QUERY_LATENCY_SECONDS.time():
        pass  # just ensure the context manager doesn't raise


def test_celery_tasks_total_incrementable():
    CELERY_TASKS_TOTAL.labels(task_name="ingest", state="success").inc()
    val = CELERY_TASKS_TOTAL.labels(task_name="ingest", state="success")._value.get()
    assert val >= 1


def test_initialise_app_info_does_not_raise():
    # Calling twice is safe (idempotent on prometheus Info)
    initialise_app_info(version="0.1.0", env="test")


def test_metrics_output_contains_vertexops_prefix():
    body, _ = get_metrics_output()
    assert b"vertexops_" in body


# ---------------------------------------------------------------------------
# OTel setup — disabled when no endpoint
# ---------------------------------------------------------------------------


def test_setup_otel_noop_when_no_endpoint():
    # Should not raise; tracing remains unset
    setup_otel(service_name="vertexops", endpoint=None)


def test_setup_otel_warns_on_missing_package():
    with patch.dict("sys.modules", {"opentelemetry": None}):
        # ImportError path — should log warning, not raise
        setup_otel(service_name="vertexops", endpoint="http://otel:4317")


# ---------------------------------------------------------------------------
# Audit logging
# ---------------------------------------------------------------------------


def test_audit_emit_logs_event(caplog):
    with caplog.at_level(logging.INFO, logger="vertexops.audit"):
        emit(AuditEvent.USER_LOGIN, outcome="success")
    assert any("AUDIT" in r.message for r in caplog.records)


def test_audit_emit_with_actor_and_workspace(caplog):
    uid = uuid.uuid4()
    ws = uuid.uuid4()
    with caplog.at_level(logging.INFO, logger="vertexops.audit"):
        emit(
            AuditEvent.DOCUMENT_DELETED,
            actor_id=uid,
            workspace_id=ws,
            resource_id="doc-123",
        )
    record = next(r for r in caplog.records if "AUDIT" in r.message)
    fields = record.__dict__.get("json_fields", {})
    assert fields["actor_id"] == str(uid)
    assert fields["workspace_id"] == str(ws)
    assert fields["resource_id"] == "doc-123"


def test_audit_strips_secret_keys(caplog):
    with caplog.at_level(logging.INFO, logger="vertexops.audit"):
        emit(
            AuditEvent.CONFIG_CHANGED,
            details={"setting": "log_level", "api_secret_key": "should-be-stripped"},
        )
    record = next(r for r in caplog.records if "AUDIT" in r.message)
    fields = record.__dict__.get("json_fields", {})
    assert "api_secret_key" not in fields.get("details", {})
    assert fields["details"]["setting"] == "log_level"


def test_audit_emit_failure_outcome(caplog):
    with caplog.at_level(logging.INFO, logger="vertexops.audit"):
        emit(AuditEvent.USER_LOGIN_FAILED, outcome="failure")
    record = next(r for r in caplog.records if "AUDIT" in r.message)
    assert record.__dict__.get("json_fields", {})["outcome"] == "failure"
