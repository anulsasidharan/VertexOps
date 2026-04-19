"""Abstract storage backend interface and shared data types."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from uuid import UUID

# ---------------------------------------------------------------------------
# Shared data types
# ---------------------------------------------------------------------------


@dataclass
class UploadSpec:
    """Describes how a client should upload a file directly to storage.

    For GCS this carries a signed URL; for the local adapter it carries the
    absolute file-system path the API will write to on the caller's behalf.
    """

    upload_url: str
    storage_key: str
    storage_uri: str
    method: str = "PUT"
    headers: dict[str, str] = field(default_factory=dict)
    expires_in: int = 3600


# ---------------------------------------------------------------------------
# Abstract backend
# ---------------------------------------------------------------------------


class StorageBackend(ABC):
    """Provider-agnostic interface for object storage operations.

    All I/O methods are async.  Adapters that talk to sync SDKs (e.g. the
    local filesystem) must delegate blocking work to a thread pool.
    """

    @abstractmethod
    async def put(
        self,
        key: str,
        data: bytes,
        content_type: str = "application/octet-stream",
    ) -> str:
        """Upload *data* under *key*.  Returns the canonical storage URI."""

    @abstractmethod
    async def get(self, key: str) -> bytes:
        """Download and return the raw bytes stored under *key*."""

    @abstractmethod
    async def delete(self, key: str) -> None:
        """Permanently remove the object at *key*."""

    @abstractmethod
    async def exists(self, key: str) -> bool:
        """Return ``True`` if an object exists at *key*."""

    @abstractmethod
    async def prepare_upload(
        self,
        key: str,
        content_type: str = "application/octet-stream",
        expires_in: int = 3600,
    ) -> UploadSpec:
        """Return an :class:`UploadSpec` the caller can use to upload directly.

        For GCS this is a signed URL; for the local adapter it is the
        absolute path on disk (dev only).
        """

    @abstractmethod
    def storage_uri(self, key: str) -> str:
        """Return the canonical URI for a stored object without fetching it."""


# ---------------------------------------------------------------------------
# Key-generation helpers
# ---------------------------------------------------------------------------


def document_storage_key(workspace_id: UUID, document_id: UUID, filename: str) -> str:
    """Canonical storage key for a raw document upload."""
    return f"documents/{workspace_id}/{document_id}/{filename}"


def artifact_storage_key(run_id: UUID, filename: str) -> str:
    """Canonical storage key for an experiment/eval artifact."""
    return f"artifacts/{run_id}/{filename}"
