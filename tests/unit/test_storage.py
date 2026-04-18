"""Unit tests for object storage abstraction."""

import uuid
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend.core.exceptions import NotFoundError
from backend.ingestion.storage.base import (
    StorageBackend,
    UploadSpec,
    artifact_storage_key,
    document_storage_key,
)
from backend.ingestion.storage.local import LocalStorageBackend
from backend.ingestion.storage.service import _create_backend, get_storage_backend
import backend.ingestion.storage.service as svc_module


# ---------------------------------------------------------------------------
# UploadSpec
# ---------------------------------------------------------------------------


def test_upload_spec_fields():
    spec = UploadSpec(
        upload_url="https://example.com/upload",
        storage_key="documents/abc/def/file.pdf",
        storage_uri="gs://bucket/documents/abc/def/file.pdf",
        method="PUT",
        headers={"Content-Type": "application/pdf"},
        expires_in=3600,
    )
    assert spec.upload_url == "https://example.com/upload"
    assert spec.storage_key == "documents/abc/def/file.pdf"
    assert spec.method == "PUT"
    assert spec.expires_in == 3600


def test_upload_spec_defaults():
    spec = UploadSpec(
        upload_url="/tmp/foo",
        storage_key="foo",
        storage_uri="file:///tmp/foo",
    )
    assert spec.method == "PUT"
    assert spec.headers == {}
    assert spec.expires_in == 3600


# ---------------------------------------------------------------------------
# Key-generation helpers
# ---------------------------------------------------------------------------


def test_document_storage_key_format():
    ws_id = uuid.UUID("00000000-0000-0000-0000-000000000001")
    doc_id = uuid.UUID("00000000-0000-0000-0000-000000000002")
    key = document_storage_key(ws_id, doc_id, "report.pdf")
    assert key == f"documents/{ws_id}/{doc_id}/report.pdf"


def test_artifact_storage_key_format():
    run_id = uuid.UUID("00000000-0000-0000-0000-000000000003")
    key = artifact_storage_key(run_id, "metrics.json")
    assert key == f"artifacts/{run_id}/metrics.json"


def test_document_storage_key_preserves_filename():
    ws = uuid.uuid4()
    doc = uuid.uuid4()
    key = document_storage_key(ws, doc, "my file (v2).docx")
    assert key.endswith("/my file (v2).docx")


# ---------------------------------------------------------------------------
# LocalStorageBackend — filesystem operations
# ---------------------------------------------------------------------------


@pytest.fixture
def local_backend(tmp_path: Path) -> LocalStorageBackend:
    return LocalStorageBackend(str(tmp_path))


@pytest.mark.asyncio
async def test_local_put_returns_uri(local_backend: LocalStorageBackend):
    uri = await local_backend.put("test/hello.txt", b"hello world")
    assert uri.startswith("file:///")
    assert "hello.txt" in uri


@pytest.mark.asyncio
async def test_local_put_creates_parent_dirs(local_backend: LocalStorageBackend, tmp_path: Path):
    await local_backend.put("deep/nested/dir/file.bin", b"\x00\x01\x02")
    assert (tmp_path / "deep" / "nested" / "dir" / "file.bin").exists()


@pytest.mark.asyncio
async def test_local_put_and_get_round_trip(local_backend: LocalStorageBackend):
    payload = b"round-trip payload"
    await local_backend.put("docs/payload.bin", payload)
    result = await local_backend.get("docs/payload.bin")
    assert result == payload


@pytest.mark.asyncio
async def test_local_get_missing_raises(local_backend: LocalStorageBackend):
    with pytest.raises(NotFoundError):
        await local_backend.get("nonexistent/file.txt")


@pytest.mark.asyncio
async def test_local_exists_true(local_backend: LocalStorageBackend):
    await local_backend.put("presence/check.txt", b"data")
    assert await local_backend.exists("presence/check.txt") is True


@pytest.mark.asyncio
async def test_local_exists_false(local_backend: LocalStorageBackend):
    assert await local_backend.exists("does/not/exist.txt") is False


@pytest.mark.asyncio
async def test_local_delete_removes_file(local_backend: LocalStorageBackend, tmp_path: Path):
    await local_backend.put("to_delete.txt", b"bye")
    await local_backend.delete("to_delete.txt")
    assert not (tmp_path / "to_delete.txt").exists()


@pytest.mark.asyncio
async def test_local_delete_missing_is_noop(local_backend: LocalStorageBackend):
    # Should not raise when the file does not exist
    await local_backend.delete("ghost/file.txt")


@pytest.mark.asyncio
async def test_local_prepare_upload_returns_spec(local_backend: LocalStorageBackend):
    spec = await local_backend.prepare_upload("docs/upload.pdf", "application/pdf")
    assert isinstance(spec, UploadSpec)
    assert spec.storage_key == "docs/upload.pdf"
    assert spec.method == "PUT"
    assert spec.storage_uri.startswith("file:///")
    assert "upload.pdf" in spec.storage_uri


@pytest.mark.asyncio
async def test_local_prepare_upload_respects_expires_in(local_backend: LocalStorageBackend):
    spec = await local_backend.prepare_upload("k", expires_in=7200)
    assert spec.expires_in == 7200


def test_local_storage_uri_format(local_backend: LocalStorageBackend):
    uri = local_backend.storage_uri("some/key.txt")
    assert uri.startswith("file:///")
    assert "key.txt" in uri


def test_local_path_traversal_blocked(local_backend: LocalStorageBackend):
    with pytest.raises(ValueError, match="escapes base directory"):
        local_backend._abs("../../etc/passwd")


# ---------------------------------------------------------------------------
# LocalStorageBackend — overwrite behaviour
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_local_put_overwrites_existing(local_backend: LocalStorageBackend):
    await local_backend.put("overwrite.txt", b"original")
    await local_backend.put("overwrite.txt", b"updated")
    data = await local_backend.get("overwrite.txt")
    assert data == b"updated"


# ---------------------------------------------------------------------------
# StorageBackend is abstract
# ---------------------------------------------------------------------------


def test_storage_backend_is_abstract():
    import inspect

    assert inspect.isabstract(StorageBackend)


# ---------------------------------------------------------------------------
# GCSStorageBackend — interface shape (mocked)
# ---------------------------------------------------------------------------


def test_gcs_storage_uri_format():
    from backend.ingestion.storage.gcs import GCSStorageBackend

    backend = GCSStorageBackend("my-bucket")
    assert backend.storage_uri("docs/file.pdf") == "gs://my-bucket/docs/file.pdf"


@pytest.mark.asyncio
async def test_gcs_put_calls_upload(tmp_path: Path):
    from backend.ingestion.storage.gcs import GCSStorageBackend

    backend = GCSStorageBackend("test-bucket")
    mock_blob = MagicMock()
    mock_bucket = MagicMock()
    mock_bucket.blob.return_value = mock_blob
    backend._GCSStorageBackend__client = MagicMock()
    backend._GCSStorageBackend__client.bucket.return_value = mock_bucket

    uri = await backend.put("key.txt", b"data", "text/plain")

    mock_blob.upload_from_string.assert_called_once_with(b"data", content_type="text/plain")
    assert uri == "gs://test-bucket/key.txt"


@pytest.mark.asyncio
async def test_gcs_get_calls_download():
    from backend.ingestion.storage.gcs import GCSStorageBackend

    backend = GCSStorageBackend("test-bucket")
    mock_blob = MagicMock()
    mock_blob.exists.return_value = True
    mock_blob.download_as_bytes.return_value = b"content"
    mock_bucket = MagicMock()
    mock_bucket.blob.return_value = mock_blob
    backend._GCSStorageBackend__client = MagicMock()
    backend._GCSStorageBackend__client.bucket.return_value = mock_bucket

    result = await backend.get("key.txt")
    assert result == b"content"


@pytest.mark.asyncio
async def test_gcs_get_missing_raises():
    from backend.ingestion.storage.gcs import GCSStorageBackend

    backend = GCSStorageBackend("test-bucket")
    mock_blob = MagicMock()
    mock_blob.exists.return_value = False
    mock_bucket = MagicMock()
    mock_bucket.blob.return_value = mock_blob
    backend._GCSStorageBackend__client = MagicMock()
    backend._GCSStorageBackend__client.bucket.return_value = mock_bucket

    with pytest.raises(NotFoundError):
        await backend.get("missing.txt")


@pytest.mark.asyncio
async def test_gcs_delete_calls_blob_delete():
    from backend.ingestion.storage.gcs import GCSStorageBackend

    backend = GCSStorageBackend("test-bucket")
    mock_blob = MagicMock()
    mock_blob.exists.return_value = True
    mock_bucket = MagicMock()
    mock_bucket.blob.return_value = mock_blob
    backend._GCSStorageBackend__client = MagicMock()
    backend._GCSStorageBackend__client.bucket.return_value = mock_bucket

    await backend.delete("some/key.txt")
    mock_blob.delete.assert_called_once()


@pytest.mark.asyncio
async def test_gcs_exists_delegates_to_blob():
    from backend.ingestion.storage.gcs import GCSStorageBackend

    backend = GCSStorageBackend("test-bucket")
    mock_blob = MagicMock()
    mock_blob.exists.return_value = True
    mock_bucket = MagicMock()
    mock_bucket.blob.return_value = mock_blob
    backend._GCSStorageBackend__client = MagicMock()
    backend._GCSStorageBackend__client.bucket.return_value = mock_bucket

    assert await backend.exists("key.txt") is True


@pytest.mark.asyncio
async def test_gcs_prepare_upload_returns_spec():
    from backend.ingestion.storage.gcs import GCSStorageBackend

    backend = GCSStorageBackend("test-bucket")
    mock_blob = MagicMock()
    mock_blob.generate_signed_url.return_value = "https://storage.googleapis.com/signed"
    mock_bucket = MagicMock()
    mock_bucket.blob.return_value = mock_blob
    backend._GCSStorageBackend__client = MagicMock()
    backend._GCSStorageBackend__client.bucket.return_value = mock_bucket

    spec = await backend.prepare_upload("doc.pdf", "application/pdf", expires_in=600)

    assert isinstance(spec, UploadSpec)
    assert spec.upload_url == "https://storage.googleapis.com/signed"
    assert spec.storage_uri == "gs://test-bucket/doc.pdf"
    assert spec.headers["Content-Type"] == "application/pdf"
    assert spec.expires_in == 600


def test_gcs_missing_sdk_raises_import_error():
    from backend.ingestion.storage import gcs as gcs_module

    original = gcs_module._GCS_AVAILABLE
    try:
        with patch.dict("sys.modules", {"google.cloud": None, "google.cloud.storage": None}):
            gcs_module._GCS_AVAILABLE = None
            with pytest.raises(ImportError, match="google-cloud-storage"):
                gcs_module._require_gcs()
    finally:
        gcs_module._GCS_AVAILABLE = original


# ---------------------------------------------------------------------------
# get_storage_backend factory
# ---------------------------------------------------------------------------


def test_factory_returns_local_by_default():
    svc_module._backend = None
    settings = MagicMock()
    settings.storage_backend = "local"
    settings.storage_local_path = "/tmp/vertexops-test"

    with patch("backend.core.config.get_settings", return_value=settings):
        backend = _create_backend()

    assert isinstance(backend, LocalStorageBackend)
    svc_module._backend = None


def test_factory_returns_local_when_gcs_bucket_missing():
    svc_module._backend = None
    settings = MagicMock()
    settings.storage_backend = "gcs"
    settings.gcs_bucket_name = None
    settings.storage_local_path = "/tmp/vertexops-test"

    with patch("backend.core.config.get_settings", return_value=settings):
        backend = _create_backend()

    assert isinstance(backend, LocalStorageBackend)
    svc_module._backend = None


def test_factory_returns_gcs_when_configured():
    from backend.ingestion.storage.gcs import GCSStorageBackend

    svc_module._backend = None
    settings = MagicMock()
    settings.storage_backend = "gcs"
    settings.gcs_bucket_name = "prod-bucket"
    settings.storage_local_path = "/tmp"

    with patch("backend.core.config.get_settings", return_value=settings):
        backend = _create_backend()

    assert isinstance(backend, GCSStorageBackend)
    svc_module._backend = None


def test_get_storage_backend_singleton():
    svc_module._backend = None
    settings = MagicMock()
    settings.storage_backend = "local"
    settings.storage_local_path = "/tmp/vertexops-test"

    with patch("backend.core.config.get_settings", return_value=settings):
        a = get_storage_backend()
        b = get_storage_backend()

    assert a is b
    svc_module._backend = None
