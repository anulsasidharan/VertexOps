"""Integration tests for the Documents API endpoints."""

import uuid
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

from fastapi.testclient import TestClient

from backend.api.dependencies import get_current_user
from backend.api.dependencies.auth import AuthContext
from backend.api.v1.documents import get_document_service
from backend.core.exceptions import ForbiddenError, NotFoundError
from backend.ingestion.services import DocumentService
from backend.ingestion.storage.base import UploadSpec
from backend.main import app

_WS_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")
_USER_ID = uuid.UUID("00000000-0000-0000-0000-000000000002")
_DOC_ID = uuid.UUID("00000000-0000-0000-0000-000000000003")
_NOW = datetime(2026, 4, 17, 12, 0, 0)


def _auth(workspace_id=_WS_ID):
    return AuthContext(user_id=_USER_ID, role="member", workspace_id=workspace_id, auth_type="jwt")


def _make_doc(**kwargs):
    doc = MagicMock()
    doc.id = kwargs.get("id", _DOC_ID)
    doc.workspace_id = kwargs.get("workspace_id", _WS_ID)
    doc.title = kwargs.get("title", "Test Document")
    doc.source_uri = kwargs.get("source_uri", None)
    doc.format = kwargs.get("format", "pdf")
    doc.language = kwargs.get("language", "en")
    doc.content_hash = kwargs.get("content_hash", None)
    doc.ingest_status = kwargs.get("ingest_status", "pending")
    doc.doc_metadata = kwargs.get("doc_metadata", None)
    doc.created_at = _NOW
    doc.updated_at = _NOW
    return doc


def _make_svc():
    svc = MagicMock(spec=DocumentService)
    svc.register = AsyncMock(return_value=_make_doc())
    svc.prepare_upload = AsyncMock(
        return_value=(
            _make_doc(),
            UploadSpec(
                upload_url="file:///tmp/key.pdf",
                storage_key="documents/ws/doc/file.pdf",
                storage_uri="file:///tmp/key.pdf",
            ),
        )
    )
    svc.complete_upload = AsyncMock(return_value=_make_doc(ingest_status="uploaded"))
    svc.list = AsyncMock(return_value=([_make_doc()], 1))
    svc.get = AsyncMock(return_value=_make_doc())
    svc.delete = AsyncMock(return_value=None)
    return svc


client = TestClient(app, raise_server_exceptions=False)


# ---------------------------------------------------------------------------
# POST /documents — register
# ---------------------------------------------------------------------------


class TestRegisterDocument:
    def setup_method(self):
        self._svc = _make_svc()
        app.dependency_overrides[get_current_user] = lambda: _auth()
        app.dependency_overrides[get_document_service] = lambda: self._svc

    def teardown_method(self):
        app.dependency_overrides.clear()

    def test_register_returns_201(self):
        resp = client.post("/api/v1/documents", json={"title": "My Doc", "format": "pdf"})
        assert resp.status_code == 201
        body = resp.json()
        assert body["id"] == str(_DOC_ID)
        assert body["ingest_status"] == "pending"

    def test_register_response_shape(self):
        resp = client.post("/api/v1/documents", json={})
        body = resp.json()
        for field in ("id", "workspace_id", "ingest_status", "created_at", "updated_at"):
            assert field in body

    def test_register_calls_service_with_correct_workspace(self):
        client.post("/api/v1/documents", json={"title": "Doc"})
        self._svc.register.assert_awaited_once()
        assert self._svc.register.call_args[0][0] == _WS_ID

    def test_register_unauthenticated_returns_401(self):
        app.dependency_overrides.clear()
        resp = client.post("/api/v1/documents", json={"title": "Doc"})
        assert resp.status_code == 401

    def test_register_no_workspace_returns_403(self):
        app.dependency_overrides[get_current_user] = lambda: _auth(workspace_id=None)
        resp = client.post("/api/v1/documents", json={"title": "Doc"})
        assert resp.status_code == 403
        assert resp.json()["error"]["code"] == "FORBIDDEN"


# ---------------------------------------------------------------------------
# POST /documents/upload-url — prepare upload
# ---------------------------------------------------------------------------


class TestPrepareUpload:
    def setup_method(self):
        self._svc = _make_svc()
        app.dependency_overrides[get_current_user] = lambda: _auth()
        app.dependency_overrides[get_document_service] = lambda: self._svc

    def teardown_method(self):
        app.dependency_overrides.clear()

    def test_prepare_upload_returns_201(self):
        resp = client.post(
            "/api/v1/documents/upload-url",
            json={"filename": "report.pdf", "content_type": "application/pdf"},
        )
        assert resp.status_code == 201
        body = resp.json()
        assert body["document_id"] == str(_DOC_ID)
        assert "upload_url" in body
        assert "storage_key" in body
        assert "storage_uri" in body
        assert "method" in body
        assert "expires_in" in body

    def test_prepare_upload_unauthenticated_returns_401(self):
        app.dependency_overrides.clear()
        resp = client.post(
            "/api/v1/documents/upload-url",
            json={"filename": "report.pdf"},
        )
        assert resp.status_code == 401

    def test_prepare_upload_no_workspace_returns_403(self):
        app.dependency_overrides[get_current_user] = lambda: _auth(workspace_id=None)
        resp = client.post(
            "/api/v1/documents/upload-url",
            json={"filename": "report.pdf"},
        )
        assert resp.status_code == 403

    def test_prepare_upload_missing_filename_returns_422(self):
        resp = client.post("/api/v1/documents/upload-url", json={})
        assert resp.status_code == 422


# ---------------------------------------------------------------------------
# POST /documents/{id}/complete — complete upload
# ---------------------------------------------------------------------------


class TestCompleteUpload:
    def setup_method(self):
        self._svc = _make_svc()
        app.dependency_overrides[get_current_user] = lambda: _auth()
        app.dependency_overrides[get_document_service] = lambda: self._svc

    def teardown_method(self):
        app.dependency_overrides.clear()

    def test_complete_upload_returns_200(self):
        resp = client.post(
            f"/api/v1/documents/{_DOC_ID}/complete",
            json={"content_hash": "sha256abc"},
        )
        assert resp.status_code == 200
        assert resp.json()["ingest_status"] == "uploaded"

    def test_complete_upload_not_found_returns_404(self):
        self._svc.complete_upload = AsyncMock(side_effect=NotFoundError("Document not found."))
        resp = client.post(f"/api/v1/documents/{_DOC_ID}/complete", json={})
        assert resp.status_code == 404
        assert resp.json()["error"]["code"] == "NOT_FOUND"

    def test_complete_upload_unauthenticated_returns_401(self):
        app.dependency_overrides.clear()
        resp = client.post(f"/api/v1/documents/{_DOC_ID}/complete", json={})
        assert resp.status_code == 401


# ---------------------------------------------------------------------------
# GET /documents — list
# ---------------------------------------------------------------------------


class TestListDocuments:
    def setup_method(self):
        self._svc = _make_svc()
        app.dependency_overrides[get_current_user] = lambda: _auth()
        app.dependency_overrides[get_document_service] = lambda: self._svc

    def teardown_method(self):
        app.dependency_overrides.clear()

    def test_list_returns_200_with_envelope(self):
        resp = client.get("/api/v1/documents")
        assert resp.status_code == 200
        body = resp.json()
        assert "items" in body
        assert "total" in body
        assert "limit" in body
        assert "offset" in body

    def test_list_default_pagination(self):
        resp = client.get("/api/v1/documents")
        body = resp.json()
        assert body["total"] == 1
        assert body["limit"] == 50
        assert body["offset"] == 0
        assert len(body["items"]) == 1

    def test_list_custom_pagination(self):
        self._svc.list = AsyncMock(return_value=([], 0))
        resp = client.get("/api/v1/documents?limit=10&offset=20")
        assert resp.status_code == 200
        call_args = self._svc.list.call_args[0]
        assert call_args[2] == 10  # limit
        assert call_args[3] == 20  # offset

    def test_list_status_filter_forwarded(self):
        self._svc.list = AsyncMock(return_value=([], 0))
        client.get("/api/v1/documents?status=uploaded")
        assert self._svc.list.call_args[0][1] == "uploaded"

    def test_list_empty_result(self):
        self._svc.list = AsyncMock(return_value=([], 0))
        resp = client.get("/api/v1/documents")
        body = resp.json()
        assert body["total"] == 0
        assert body["items"] == []

    def test_list_unauthenticated_returns_401(self):
        app.dependency_overrides.clear()
        resp = client.get("/api/v1/documents")
        assert resp.status_code == 401


# ---------------------------------------------------------------------------
# GET /documents/{id} — get single document
# ---------------------------------------------------------------------------


class TestGetDocument:
    def setup_method(self):
        self._svc = _make_svc()
        app.dependency_overrides[get_current_user] = lambda: _auth()
        app.dependency_overrides[get_document_service] = lambda: self._svc

    def teardown_method(self):
        app.dependency_overrides.clear()

    def test_get_returns_200(self):
        resp = client.get(f"/api/v1/documents/{_DOC_ID}")
        assert resp.status_code == 200
        assert resp.json()["id"] == str(_DOC_ID)

    def test_get_response_includes_all_fields(self):
        resp = client.get(f"/api/v1/documents/{_DOC_ID}")
        body = resp.json()
        for field in ("id", "workspace_id", "title", "ingest_status", "created_at"):
            assert field in body

    def test_get_not_found_returns_404(self):
        self._svc.get = AsyncMock(side_effect=NotFoundError("Document not found."))
        resp = client.get(f"/api/v1/documents/{_DOC_ID}")
        assert resp.status_code == 404
        assert resp.json()["error"]["code"] == "NOT_FOUND"

    def test_get_forbidden_returns_403(self):
        self._svc.get = AsyncMock(
            side_effect=ForbiddenError("Document does not belong to this workspace.")
        )
        resp = client.get(f"/api/v1/documents/{_DOC_ID}")
        assert resp.status_code == 403
        assert resp.json()["error"]["code"] == "FORBIDDEN"

    def test_get_unauthenticated_returns_401(self):
        app.dependency_overrides.clear()
        resp = client.get(f"/api/v1/documents/{_DOC_ID}")
        assert resp.status_code == 401


# ---------------------------------------------------------------------------
# DELETE /documents/{id}
# ---------------------------------------------------------------------------


class TestDeleteDocument:
    def setup_method(self):
        self._svc = _make_svc()
        app.dependency_overrides[get_current_user] = lambda: _auth()
        app.dependency_overrides[get_document_service] = lambda: self._svc

    def teardown_method(self):
        app.dependency_overrides.clear()

    def test_delete_returns_204_with_empty_body(self):
        resp = client.delete(f"/api/v1/documents/{_DOC_ID}")
        assert resp.status_code == 204
        assert resp.content == b""

    def test_delete_calls_service_with_correct_ids(self):
        client.delete(f"/api/v1/documents/{_DOC_ID}")
        self._svc.delete.assert_awaited_once()
        call_ws, call_doc = self._svc.delete.call_args[0]
        assert call_ws == _WS_ID
        assert call_doc == _DOC_ID

    def test_delete_not_found_returns_404(self):
        self._svc.delete = AsyncMock(side_effect=NotFoundError("Document not found."))
        resp = client.delete(f"/api/v1/documents/{_DOC_ID}")
        assert resp.status_code == 404

    def test_delete_unauthenticated_returns_401(self):
        app.dependency_overrides.clear()
        resp = client.delete(f"/api/v1/documents/{_DOC_ID}")
        assert resp.status_code == 401
