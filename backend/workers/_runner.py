"""Async runner functions called by Celery tasks via asyncio.run().

Each function opens its own DB session so it can run inside a sync Celery worker.
"""

import logging
import uuid
from typing import Any

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


async def run_parse_document(document_id: uuid.UUID, workspace_id: uuid.UUID) -> dict[str, Any]:
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


async def run_embed_document(document_id: uuid.UUID, workspace_id: uuid.UUID) -> dict[str, Any]:
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


async def run_build_index(index_id: uuid.UUID, workspace_id: uuid.UUID) -> dict[str, Any]:
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


async def run_eval(run_id: uuid.UUID) -> dict[str, Any]:
    """Aggregate eval metrics, write JSON/HTML report artifacts, finalize run status."""
    import json
    from datetime import datetime, timezone

    from backend.evaluation.service import EvaluationService
    from backend.experiments.tracking.mlflow_tracker import try_log_evaluation_to_mlflow
    from backend.ingestion.storage.base import artifact_storage_key
    from backend.ingestion.storage.service import get_storage_backend
    from backend.repositories.run_repository import RunRepository

    factory = get_session_factory()
    storage = get_storage_backend()
    json_key = artifact_storage_key(run_id, "report.json")
    html_key = artifact_storage_key(run_id, "report.html")

    async with factory() as session:
        probe = await RunRepository(session).get(run_id)
    if probe is None:
        logger.error("run_eval: run %s not found", run_id)
        return {"run_id": str(run_id), "status": "missing"}

    exp_id_str = str(probe.experiment_id)
    eval_kind = str((probe.run_logs or {}).get("kind", ""))
    metrics_for_ml: dict[str, Any] = {}

    try:
        async with factory() as session:
            async with session.begin():
                run_repo = RunRepository(session)
                eval_svc = EvaluationService(session)
                run = await run_repo.get(run_id)
                if run is None:
                    logger.error("run_eval: run %s disappeared", run_id)
                    return {"run_id": str(run_id), "status": "missing"}

                now = datetime.now(timezone.utc)
                run.status = "running"
                run.started_at = now
                await session.flush()

                snap = await eval_svc.compute_and_save_aggregate(run_id)
                report: dict[str, Any] = {
                    "run_id": str(run_id),
                    "experiment_id": str(run.experiment_id),
                    "metrics": snap.snapshot_metrics or {},
                    "generated_at": now.isoformat(),
                }
                json_body = json.dumps(report, indent=2).encode("utf-8")
                html_body = (
                    '<!DOCTYPE html><html><head><meta charset="utf-8"/>'
                    "<title>Evaluation report</title></head><body><pre>"
                    f"{json.dumps(report, indent=2)}"
                    "</pre></body></html>"
                ).encode()

                json_uri = await storage.put(json_key, json_body, "application/json")
                await storage.put(html_key, html_body, "text/html; charset=utf-8")

                done = datetime.now(timezone.utc)
                run.status = "completed"
                run.finished_at = done
                run.artifact_uri = json_uri
                run.run_logs = {
                    **(run.run_logs or {}),
                    "artifact_key": json_key,
                    "artifact_html_key": html_key,
                }
                metrics_for_ml = dict(snap.snapshot_metrics or {})

        try_log_evaluation_to_mlflow(
            run_id=str(run_id),
            experiment_id=exp_id_str,
            metrics=metrics_for_ml,
            params={"eval_kind": eval_kind},
        )

        if eval_kind == "evaluation":
            from backend.integrations.notifications.service import dispatch_notification

            dispatch_notification(
                "eval_completed",
                {
                    "run_id": str(run_id),
                    "experiment_id": exp_id_str,
                    "status": "completed",
                },
            )

            from backend.integrations.billing.service import record_usage_event

            qty = 1.0
            for key in ("total_tokens", "prompt_tokens", "completion_tokens"):
                raw = metrics_for_ml.get(key)
                if raw is not None:
                    try:
                        qty = float(raw)
                    except (TypeError, ValueError):
                        qty = 1.0
                    break
            record_usage_event(
                "eval_completion",
                qty,
                metadata={"run_id": str(run_id), "experiment_id": exp_id_str},
            )

        logger.info("run_eval: completed run=%s", run_id)
        return {"run_id": str(run_id), "status": "completed"}
    except Exception as exc:
        logger.exception("run_eval: failed run=%s", run_id)
        async with factory() as session:
            async with session.begin():
                run_repo = RunRepository(session)
                run = await run_repo.get(run_id)
                if run is not None:
                    run.status = "failed"
                    run.finished_at = datetime.now(timezone.utc)
                    run.run_logs = {
                        **(run.run_logs or {}),
                        "error": str(exc)[:500],
                    }
        return {"run_id": str(run_id), "status": "failed"}
