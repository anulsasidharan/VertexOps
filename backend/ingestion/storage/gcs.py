"""Google Cloud Storage backend — production adapter.

The ``google-cloud-storage`` package is imported lazily so that the module
can be imported in environments where the package is absent (e.g. local dev
without GCP dependencies).  Methods raise ``ImportError`` clearly if the
SDK is missing at call time.
"""

import asyncio
import datetime
from typing import TYPE_CHECKING, Any, Optional

from backend.ingestion.storage.base import StorageBackend, UploadSpec
from backend.core.exceptions import NotFoundError

if TYPE_CHECKING:
    from google.cloud import storage as gcs_storage

_GCS_AVAILABLE: Optional[bool] = None


def _require_gcs() -> Any:
    global _GCS_AVAILABLE
    try:
        from google.cloud import storage as _gcs

        _GCS_AVAILABLE = True
        return _gcs
    except ImportError:
        _GCS_AVAILABLE = False
        raise ImportError(
            "google-cloud-storage is required for the GCS storage backend. "
            "Install it with: pip install google-cloud-storage"
        )


class GCSStorageBackend(StorageBackend):
    """Cloud Storage backend backed by Google Cloud Storage.

    Requires ``GOOGLE_APPLICATION_CREDENTIALS`` or Workload Identity to be
    configured in the runtime environment.  In production this is handled
    via GCP IAM; in staging a service-account key file may be used.
    """

    def __init__(self, bucket_name: str) -> None:
        self._bucket_name = bucket_name
        self.__client: Optional[Any] = None

    def _client(self) -> Any:
        if self.__client is None:
            gcs = _require_gcs()
            self.__client = gcs.Client()
        return self.__client

    def _bucket(self) -> Any:
        return self._client().bucket(self._bucket_name)

    # ------------------------------------------------------------------
    # StorageBackend interface
    # ------------------------------------------------------------------

    async def put(
        self,
        key: str,
        data: bytes,
        content_type: str = "application/octet-stream",
    ) -> str:
        def _upload() -> None:
            blob = self._bucket().blob(key)
            blob.upload_from_string(data, content_type=content_type)

        await asyncio.to_thread(_upload)
        return self.storage_uri(key)

    async def get(self, key: str) -> bytes:
        def _download() -> bytes:
            blob = self._bucket().blob(key)
            if not blob.exists():
                raise NotFoundError(f"Object not found in GCS: {key!r}")
            return blob.download_as_bytes()

        return await asyncio.to_thread(_download)

    async def delete(self, key: str) -> None:
        def _delete() -> None:
            blob = self._bucket().blob(key)
            if blob.exists():
                blob.delete()

        await asyncio.to_thread(_delete)

    async def exists(self, key: str) -> bool:
        def _exists() -> bool:
            return self._bucket().blob(key).exists()

        return await asyncio.to_thread(_exists)

    async def prepare_upload(
        self,
        key: str,
        content_type: str = "application/octet-stream",
        expires_in: int = 3600,
    ) -> UploadSpec:
        def _sign() -> str:
            blob = self._bucket().blob(key)
            return blob.generate_signed_url(
                version="v4",
                expiration=datetime.timedelta(seconds=expires_in),
                method="PUT",
                content_type=content_type,
            )

        signed_url: str = await asyncio.to_thread(_sign)
        return UploadSpec(
            upload_url=signed_url,
            storage_key=key,
            storage_uri=self.storage_uri(key),
            method="PUT",
            headers={"Content-Type": content_type},
            expires_in=expires_in,
        )

    def storage_uri(self, key: str) -> str:
        return f"gs://{self._bucket_name}/{key}"
