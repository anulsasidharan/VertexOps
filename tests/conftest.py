"""Shared test fixtures and environment setup."""

import os
import uuid
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi.testclient import TestClient

# Set required env vars at import time so module-level app instantiation works.
# These are test-only values; never use in production.
_TEST_ENV = {
    "JWT_SECRET_KEY": "test-jwt-secret-key-for-unit-tests-only",
    "API_KEY_PEPPER": "test-api-key-pepper-only",
    "APP_ENV": "development",
}
for _key, _value in _TEST_ENV.items():
    os.environ.setdefault(_key, _value)

# ---------------------------------------------------------------------------
# Common UUIDs reused across test modules
# ---------------------------------------------------------------------------

WORKSPACE_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")
USER_ID = uuid.UUID("00000000-0000-0000-0000-000000000002")
DOCUMENT_ID = uuid.UUID("00000000-0000-0000-0000-000000000003")
INDEX_ID = uuid.UUID("00000000-0000-0000-0000-000000000004")
EXPERIMENT_ID = uuid.UUID("00000000-0000-0000-0000-000000000005")
RUN_ID = uuid.UUID("00000000-0000-0000-0000-000000000006")
EVAL_ID = uuid.UUID("00000000-0000-0000-0000-000000000007")
FIXED_NOW = datetime(2026, 4, 18, 12, 0, 0)


# ---------------------------------------------------------------------------
# Auth context factory
# ---------------------------------------------------------------------------


@pytest.fixture
def member_auth():
    """Return a factory that produces a member AuthContext."""
    from backend.api.dependencies.auth import AuthContext

    def _factory(workspace_id=WORKSPACE_ID, role="member"):
        return AuthContext(
            user_id=USER_ID,
            role=role,
            workspace_id=workspace_id,
            auth_type="jwt",
        )

    return _factory


@pytest.fixture
def admin_auth():
    """AuthContext with admin role."""
    from backend.api.dependencies.auth import AuthContext

    return AuthContext(
        user_id=USER_ID,
        role="admin",
        workspace_id=WORKSPACE_ID,
        auth_type="jwt",
    )


# ---------------------------------------------------------------------------
# FastAPI test client (dependency-override aware)
# ---------------------------------------------------------------------------


@pytest.fixture
def api_client():
    """Yield a TestClient that auto-clears dependency overrides after each test."""
    from backend.main import app

    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# Generic mock builders
# ---------------------------------------------------------------------------


def make_mock_document(**kwargs):
    doc = MagicMock()
    doc.id = kwargs.get("id", DOCUMENT_ID)
    doc.workspace_id = kwargs.get("workspace_id", WORKSPACE_ID)
    doc.title = kwargs.get("title", "Test Document")
    doc.source_uri = kwargs.get("source_uri", None)
    doc.format = kwargs.get("format", "pdf")
    doc.language = kwargs.get("language", "en")
    doc.content_hash = kwargs.get("content_hash", None)
    doc.ingest_status = kwargs.get("ingest_status", "pending")
    doc.doc_metadata = kwargs.get("doc_metadata", None)
    doc.created_at = FIXED_NOW
    doc.updated_at = FIXED_NOW
    return doc


def make_mock_index(**kwargs):
    idx = MagicMock()
    idx.id = kwargs.get("id", INDEX_ID)
    idx.workspace_id = kwargs.get("workspace_id", WORKSPACE_ID)
    idx.name = kwargs.get("name", "test-index")
    idx.description = kwargs.get("description", None)
    idx.status = kwargs.get("status", "ready")
    idx.index_config = kwargs.get("index_config", {"chunk_strategy": "recursive"})
    idx.config_hash = kwargs.get("config_hash", "b" * 64)
    idx.namespace = kwargs.get("namespace", "ns-test")
    idx.created_at = FIXED_NOW
    idx.updated_at = FIXED_NOW
    return idx


def make_mock_experiment(**kwargs):
    exp = MagicMock()
    exp.id = kwargs.get("id", EXPERIMENT_ID)
    exp.workspace_id = kwargs.get("workspace_id", WORKSPACE_ID)
    exp.name = kwargs.get("name", "test-experiment")
    exp.description = kwargs.get("description", None)
    exp.index_id = kwargs.get("index_id", INDEX_ID)
    exp.experiment_config = kwargs.get("experiment_config", {"top_k": 5})
    exp.config_hash = kwargs.get("config_hash", "c" * 64)
    exp.created_at = FIXED_NOW
    exp.updated_at = FIXED_NOW
    return exp


def make_mock_evaluation(**kwargs):
    ev = MagicMock()
    ev.id = kwargs.get("id", EVAL_ID)
    ev.workspace_id = kwargs.get("workspace_id", WORKSPACE_ID)
    ev.experiment_id = kwargs.get("experiment_id", EXPERIMENT_ID)
    ev.run_id = kwargs.get("run_id", RUN_ID)
    ev.status = kwargs.get("status", "pending")
    ev.total_cases = kwargs.get("total_cases", 0)
    ev.completed_cases = kwargs.get("completed_cases", 0)
    ev.metrics_summary = kwargs.get("metrics_summary", None)
    ev.artifact_uri = kwargs.get("artifact_uri", None)
    ev.created_at = FIXED_NOW
    ev.updated_at = FIXED_NOW
    return ev
