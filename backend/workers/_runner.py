"""Async runner functions called by Celery tasks via asyncio.run().

Each function opens its own DB session so it can run inside a sync Celery worker.
"""

import logging
import uuid
from typing import Any, Dict

from backend.chunking.registry import ChunkingConfig
from backend.chunking.service import ChunkingService
from backend.core.db import get_session_factory
from backend.embedding.service import EmbeddingService
from backend.ingestion.hashing import compute_content_hash
from backend.ingestion.loaders import get_loader
from backend.ingestion.storage.service import get_storage_backend
from backend.repositories.chunk_repository import ChunkRepository
from backend.repositories.document_repository import DocumentRepository
from backend.repositories.index_repository import IndexRepository
from backend.vector_store.base import VectorRecord
from backend.vector_store.service import get_vector_store

logger = logging.getLogger(__name__)


async def run_parse_document(document_id: uuid.UUID, workspace_id: uuid.UUID) -> Dict[str, Any]:
    """Fetch a document from storage, parse it, persist chunks, and update status."""
    async with get_session_factory()() as session:
        async with session.begin():
            doc_repo = DocumentRepository(session)
            doc = await doc_repo.get(document_id)
            if doc is None:
                raise ValueError(f"Document {document_id} not found")

            storage_key = (doc.doc_metadata or {}).get("storage_key")
            if not storage_key:
                doc.ingest_status = "failed"
                return {"document_id": str(document_id), "chunk_count": 0}

            storage = get_storage_backend()
            content = await storage.get(storage_key)

            filename = (doc.doc_metadata or {}).get("filename", storage_key.split("/")[-1])
            loader = get_loader(filename)
            parsed = loader.load(content, filename)

            doc.content_hash = compute_content_hash(content)
            doc.ingest_status = "parsed"

            # Delete existing chunks for retry-safety
            chunk_repo = ChunkRepository(session)
            await chunk_repo.delete_by_document(document_id)

            svc = ChunkingService()
            chunks = svc.chunk_document(
                document_id, parsed.text, ChunkingConfig(strategy="recursive")
            )
            for chunk in chunks:
                session.add(chunk)

    logger.info("Parsed doc=%s into %d chunks", document_id, len(chunks))
    return {"document_id": str(document_id), "chunk_count": len(chunks)}


async def run_embed_document(document_id: uuid.UUID, workspace_id: uuid.UUID) -> Dict[str, Any]:
    """Compute embeddings for all chunks and upsert into the vector store."""
    async with get_session_factory()() as session:
        async with session.begin():
            doc_repo = DocumentRepository(session)
            doc = await doc_repo.get(document_id)
            if doc is None:
                raise ValueError(f"Document {document_id} not found")

            chunk_repo = ChunkRepository(session)
            chunks = await chunk_repo.list_by_document(document_id)
            if not chunks:
                doc.ingest_status = "ready"
                return {"document_id": str(document_id), "vector_count": 0}

            embed_svc = EmbeddingService()
            texts = [c.text for c in chunks]
            result = await embed_svc.embed_texts(texts)

            vector_store = get_vector_store()
            namespace = str(workspace_id)
            records = [
                VectorRecord(
                    id=str(chunks[i].id),
                    vector=result.embeddings[i],
                    metadata={
                        "document_id": str(document_id),
                        "workspace_id": str(workspace_id),
                        "chunk_index": chunks[i].chunk_index,
                        "section_path": chunks[i].section_path or "",
                    },
                    namespace=namespace,
                )
                for i in range(len(chunks))
            ]

            # Update vector_id on each chunk
            for i, chunk in enumerate(chunks):
                chunk.vector_id = records[i].id

            await vector_store.upsert(records)
            doc.ingest_status = "ready"

    logger.info("Embedded doc=%s: %d vectors", document_id, len(records))
    return {"document_id": str(document_id), "vector_count": len(records)}


async def run_build_index(index_id: uuid.UUID, workspace_id: uuid.UUID) -> Dict[str, Any]:
    """Update VectorIndex status to ready after a build."""
    async with get_session_factory()() as session:
        async with session.begin():
            repo = IndexRepository(session)
            idx = await repo.get(index_id)
            if idx is None:
                raise ValueError(f"Index {index_id} not found")
            idx.status = "ready"

    logger.info("Built index=%s", index_id)
    return {"index_id": str(index_id), "status": "ready"}


async def run_eval(run_id: uuid.UUID) -> Dict[str, Any]:
    """Placeholder — evaluation runner will be implemented in Phase 5."""
    logger.info("run_eval: run=%s (placeholder)", run_id)
    return {"run_id": str(run_id), "status": "completed"}
