"""Pipeline task — end-to-end document ingest from pending to ready."""

import logging

from backend.workers.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(
    name="backend.workers.tasks.pipeline.ingest_document",
    bind=True,
    max_retries=3,
    default_retry_delay=30,
    queue="ingest",
)
def ingest_document(self, document_id: str, workspace_id: str) -> dict:
    """Orchestrate the full ingest pipeline for one document.

    Steps:
      1. Parse — fetch from storage, extract text, persist chunks
      2. Embed — compute vectors and upsert to vector store
      3. Status — document ends in ``ready`` or ``failed``

    Retry-safe: existing chunks are deleted before re-parsing.
    """
    import asyncio
    from uuid import UUID

    logger.info("ingest_document: doc=%s ws=%s", document_id, workspace_id)
    doc_uuid = UUID(document_id)
    ws_uuid = UUID(workspace_id)

    try:
        from backend.workers._runner import run_parse_document, run_embed_document

        parse_result = asyncio.run(run_parse_document(doc_uuid, ws_uuid))
        logger.info(
            "ingest_document: parse done — %d chunks", parse_result["chunk_count"]
        )

        embed_result = asyncio.run(run_embed_document(doc_uuid, ws_uuid))
        logger.info(
            "ingest_document: embed done — %d vectors", embed_result["vector_count"]
        )

        return {
            "document_id": document_id,
            "chunk_count": parse_result["chunk_count"],
            "vector_count": embed_result["vector_count"],
            "status": "ready",
        }

    except Exception as exc:
        logger.exception("ingest_document failed: %s", exc)
        # Mark document as failed before retrying
        try:
            asyncio.run(_mark_failed(doc_uuid))
        except Exception:
            pass
        raise self.retry(exc=exc)


async def _mark_failed(document_id) -> None:
    from backend.core.db import get_session_factory
    from backend.repositories.document_repository import DocumentRepository

    async with get_session_factory()() as session:
        async with session.begin():
            repo = DocumentRepository(session)
            doc = await repo.get(document_id)
            if doc:
                doc.ingest_status = "failed"
