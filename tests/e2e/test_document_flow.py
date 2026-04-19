"""E2E: Document ingestion and indexing journey.

Simulates an operator:
  1. Registering a document (metadata-only).
  2. Preparing an upload URL for the file.
  3. Completing the upload.
  4. Listing documents and confirming the record appears.
  5. Creating an index that will incorporate the document.
  6. Triggering an index rebuild.
  7. Deleting the document and confirming removal.

All external dependencies are mocked so this runs in CI without cloud infra.
"""

import uuid
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi.testclient import TestClient

from backend.api.dependencies import get_current_user
from backend.api.dependencies.auth import AuthContext
from backend.api.v1.documents import get_document_service
from backend.api.v1.indexes import get_index_service
from backend.ingestion.storage.base import UploadSpec
from backend.main import app

_WS_ID = uuid.UUID("00000000-0000-0000-0000-000000000020")
_USER_ID = uuid.UUID("00000000-0000-0000-0000-000000000021")
_DOC_ID = uuid.UUID("00000000-0000-0000-0000-000000000022")
_IDX_ID = uuid.UUID("00000000-0000-0000-0000-000000000023")
_NOW = datetime(2026, 4, 18, 12, 0, 0)


def _auth():
    return AuthContext(user_id=_USER_ID, role="member", workspace_id=_WS_ID, auth_type="jwt")


def _make_doc(**kwargs):
    doc = MagicMock()
    doc.id = kwargs.get("id", _DOC_ID)
    doc.workspace_id = _WS_ID
    doc.title = kwargs.get("title", "Architecture Overview")
    doc.source_uri = kwargs.get("source_uri", None)
    doc.format = kwargs.get("format", "pdf")
    doc.language = "en"
    doc.content_hash = kwargs.get("content_hash", None)
    doc.ingest_status = kwargs.get("ingest_status", "pending")
    doc.doc_metadata = kwargs.get("doc_metadata", None)
    doc.created_at = _NOW
    doc.updated_at = _NOW
    return doc


def _make_index(**kwargs):
    idx = MagicMock()
    idx.id = kwargs.get("id", _IDX_ID)
    idx.workspace_id = _WS_ID
    idx.name = kwargs.get("name", "prod-index")
    idx.vector_backend = "pinecone"
    idx.namespace = "ns-prod"
    idx.config_hash = "a" * 64
    idx.index_config = {"chunk_strategy": "recursive"}
    idx.status = kwargs.get("status", "ready")
    idx.created_at = _NOW
    idx.updated_at = _NOW
    return idx


def _make_doc_service():
    from backend.ingestion.services import DocumentService

    svc = MagicMock(spec=DocumentService)
    svc.register = AsyncMock(return_value=_make_doc())
    svc.prepare_upload = AsyncMock(
        return_value=(
            _make_doc(),
            UploadSpec(
                upload_url="file:///tmp/arch.pdf",
                storage_key="documents/ws/doc/arch.pdf",
                storage_uri="file:///tmp/arch.pdf",
            ),
        )
    )
    svc.complete_upload = AsyncMock(return_value=_make_doc(ingest_status="uploaded"))
    svc.list = AsyncMock(return_value=([_make_doc()], 1))
    svc.get = AsyncMock(return_value=_make_doc())
    svc.delete = AsyncMock(return_value=None)
    return svc


# ---------------------------------------------------------------------------
# Journey
# ---------------------------------------------------------------------------


class TestDocumentIngestionJourney:
    def setup_method(self):
        from unittest.mock import AsyncMock, MagicMock

        self._doc_svc = _make_doc_service()

        mock_session = AsyncMock()
        mock_session.flush = AsyncMock()
        mock_session.refresh = AsyncMock()

        building_idx = _make_index(status="building")
        self._idx_repo = MagicMock()
        self._idx_repo.session = mock_session
        self._idx_repo.add = AsyncMock(return_value=_make_index())
        self._idx_repo.list_by_workspace = AsyncMock(return_value=[_make_index()])
        self._idx_repo.get = AsyncMock(return_value=building_idx)

        app.dependency_overrides[get_current_user] = _auth
        app.dependency_overrides[get_document_service] = lambda: self._doc_svc
        app.dependency_overrides[get_index_service] = lambda: self._idx_repo

    def teardown_method(self):
        app.dependency_overrides.clear()

    def test_step1_register_document(self):
        """POST /documents creates the document record."""
        with TestClient(app) as client:
            resp = client.post(
                "/api/v1/documents",
                json={"title": "Architecture Overview", "format": "pdf"},
            )
        assert resp.status_code == 201
        body = resp.json()
        assert body["title"] == "Architecture Overview"
        assert body["ingest_status"] == "pending"

    def test_step2_prepare_upload_url(self):
        """POST /documents/upload-url returns a signed-upload descriptor."""
        with TestClient(app) as client:
            resp = client.post(
                "/api/v1/documents/upload-url",
                json={"filename": "arch.pdf", "content_type": "application/pdf"},
            )
        assert resp.status_code == 201
        body = resp.json()
        assert "upload_url" in body
        assert "storage_key" in body

    def test_step3_complete_upload(self):
        """POST /documents/{id}/complete-upload transitions status."""
        with TestClient(app) as client:
            resp = client.post(
                f"/api/v1/documents/{_DOC_ID}/complete",
                json={"storage_key": "documents/ws/doc/arch.pdf"},
            )
        assert resp.status_code == 200
        assert resp.json()["ingest_status"] == "uploaded"

    def test_step4_list_documents_shows_record(self):
        """GET /documents lists workspace documents."""
        with TestClient(app) as client:
            resp = client.get("/api/v1/documents")
        assert resp.status_code == 200
        body = resp.json()
        assert body["total"] >= 1
        assert len(body["items"]) >= 1

    def test_step5_get_document_detail(self):
        """GET /documents/{id} returns full document detail."""
        with TestClient(app) as client:
            resp = client.get(f"/api/v1/documents/{_DOC_ID}")
        assert resp.status_code == 200
        assert resp.json()["id"] == str(_DOC_ID)

    def test_step6_create_index(self):
        """POST /indexes creates a vector index."""
        with TestClient(app) as client:
            resp = client.post(
                "/api/v1/indexes",
                json={"name": "prod-index", "vector_backend": "pinecone"},
            )
        assert resp.status_code == 201

    def test_step7_trigger_index_rebuild(self):
        """POST /indexes/{id}/rebuild queues a rebuild job."""
        with TestClient(app) as client:
            resp = client.post(f"/api/v1/indexes/{_IDX_ID}/rebuild")
        assert resp.status_code in (200, 202)

    def test_step8_delete_document(self):
        """DELETE /documents/{id} removes the document."""
        with TestClient(app) as client:
            resp = client.delete(f"/api/v1/documents/{_DOC_ID}")
        assert resp.status_code == 204

    def test_unauthenticated_cannot_register(self):
        """Without auth the register endpoint blocks access."""
        app.dependency_overrides.clear()
        with TestClient(app) as client:
            resp = client.post(
                "/api/v1/documents",
                json={"title": "Sneaky Doc", "format": "txt"},
            )
        assert resp.status_code == 401
