"""Embed queue tasks — compute and upsert chunk vectors."""

import logging
from uuid import UUID

from backend.workers.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(
    name="backend.workers.tasks.embed.embed_document_chunks",
    bind=True,
    max_retries=3,
    default_retry_delay=60,
    queue="embed",
)
def embed_document_chunks(self, document_id: str, workspace_id: str) -> dict:
    """Embed all chunks for a document and upsert vectors into the vector store.

    Returns a dict with ``document_id`` and ``vector_count``.
    """
    logger.info("embed_document_chunks: doc=%s ws=%s", document_id, workspace_id)
    try:
        import asyncio
        from backend.workers._runner import run_embed_document
        result = asyncio.run(run_embed_document(UUID(document_id), UUID(workspace_id)))
        return result
    except Exception as exc:
        logger.exception("embed_document_chunks failed: %s", exc)
        raise self.retry(exc=exc)
