"""Ingest queue tasks — fetch, parse, and validate uploaded documents."""

import logging
from uuid import UUID

from backend.workers.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(
    name="backend.workers.tasks.ingest.parse_document",
    bind=True,
    max_retries=3,
    default_retry_delay=30,
    queue="ingest",
)
def parse_document(self, document_id: str, workspace_id: str) -> dict:
    """Fetch a document from storage, parse it, and persist chunks.

    Returns a dict with ``document_id`` and ``chunk_count`` for the next step.
    """
    logger.info("parse_document: doc=%s ws=%s", document_id, workspace_id)
    try:
        import asyncio

        from backend.workers._runner import run_parse_document

        result = asyncio.run(run_parse_document(UUID(document_id), UUID(workspace_id)))
        return result
    except Exception as exc:
        logger.exception("parse_document failed: %s", exc)
        raise self.retry(exc=exc)
