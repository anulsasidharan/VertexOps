"""Object storage abstraction — backends and factory."""

from backend.ingestion.storage.base import (
    StorageBackend,
    UploadSpec,
    artifact_storage_key,
    document_storage_key,
)
from backend.ingestion.storage.local import LocalStorageBackend
from backend.ingestion.storage.service import get_storage_backend

__all__ = [
    "LocalStorageBackend",
    "StorageBackend",
    "UploadSpec",
    "artifact_storage_key",
    "document_storage_key",
    "get_storage_backend",
]
