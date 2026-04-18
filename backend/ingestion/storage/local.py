"""Local filesystem storage backend — no cloud credentials required."""

import asyncio
import os
from pathlib import Path

from backend.ingestion.storage.base import StorageBackend, UploadSpec
from backend.core.exceptions import NotFoundError


class LocalStorageBackend(StorageBackend):
    """Stores objects as files under a configurable base directory.

    Suitable for local development and CI.  All blocking filesystem calls
    are run in a thread-pool executor so the async event loop is not stalled.
    """

    def __init__(self, base_path: str) -> None:
        self._base = Path(base_path).resolve()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _abs(self, key: str) -> Path:
        """Resolve *key* to an absolute path, guarding against path traversal."""
        resolved = (self._base / key).resolve()
        if not str(resolved).startswith(str(self._base)):
            raise ValueError(f"Storage key escapes base directory: {key!r}")
        return resolved

    def _storage_uri_for_path(self, path: Path) -> str:
        return path.as_uri()  # file:///...

    # ------------------------------------------------------------------
    # StorageBackend interface
    # ------------------------------------------------------------------

    async def put(
        self,
        key: str,
        data: bytes,
        content_type: str = "application/octet-stream",
    ) -> str:
        path = self._abs(key)

        def _write() -> None:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)

        await asyncio.to_thread(_write)
        return self.storage_uri(key)

    async def get(self, key: str) -> bytes:
        path = self._abs(key)

        def _read() -> bytes:
            if not path.exists():
                raise NotFoundError(f"Object not found: {key!r}")
            return path.read_bytes()

        return await asyncio.to_thread(_read)

    async def delete(self, key: str) -> None:
        path = self._abs(key)

        def _remove() -> None:
            if path.exists():
                os.remove(path)

        await asyncio.to_thread(_remove)

    async def exists(self, key: str) -> bool:
        path = self._abs(key)
        return await asyncio.to_thread(path.exists)

    async def prepare_upload(
        self,
        key: str,
        content_type: str = "application/octet-stream",
        expires_in: int = 3600,
    ) -> UploadSpec:
        """Return a local-path upload spec (dev/CI only — not a real signed URL)."""
        path = self._abs(key)
        return UploadSpec(
            upload_url=str(path),
            storage_key=key,
            storage_uri=self.storage_uri(key),
            method="PUT",
            headers={},
            expires_in=expires_in,
        )

    def storage_uri(self, key: str) -> str:
        return self._abs(key).as_uri()
