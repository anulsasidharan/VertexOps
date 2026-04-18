"""Storage service factory — selects the right backend from settings."""

import logging
from typing import Optional

from backend.ingestion.storage.base import StorageBackend
from backend.ingestion.storage.local import LocalStorageBackend

logger = logging.getLogger(__name__)

_backend: Optional[StorageBackend] = None


def get_storage_backend() -> StorageBackend:
    """Return the process-wide storage backend, creating it on first call.

    Selection logic:
    - ``storage_backend = "gcs"`` **and** ``gcs_bucket_name`` is set → GCS
    - Everything else → local filesystem (no cloud credentials needed)
    """
    global _backend
    if _backend is None:
        _backend = _create_backend()
    return _backend


def _create_backend() -> StorageBackend:
    from backend.core.config import get_settings

    settings = get_settings()

    if settings.storage_backend == "gcs":
        if not settings.gcs_bucket_name:
            logger.warning(
                "storage_backend=gcs but gcs_bucket_name is unset — "
                "falling back to local storage"
            )
            return LocalStorageBackend(settings.storage_local_path)

        from backend.ingestion.storage.gcs import GCSStorageBackend

        logger.info(
            "storage: using GCS backend (bucket=%s)", settings.gcs_bucket_name
        )
        return GCSStorageBackend(settings.gcs_bucket_name)

    logger.info("storage: using local backend (path=%s)", settings.storage_local_path)
    return LocalStorageBackend(settings.storage_local_path)
