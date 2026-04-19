"""Retrieval service — vector search, score filtering, and source normalization."""

import logging

from backend.retrieval.base import RetrievalConfig, RetrievalResult
from backend.vector_store.base import BaseVectorStore
from backend.vector_store.service import get_vector_store

logger = logging.getLogger(__name__)


class RetrievalService:
    """Retrieves relevant chunks from the vector store for a given query embedding."""

    def __init__(self, vector_store: BaseVectorStore | None = None) -> None:
        self._store = vector_store or get_vector_store()

    async def retrieve(
        self,
        query_vector: list[float],
        config: RetrievalConfig,
    ) -> list[RetrievalResult]:
        """Search the vector store and return normalized results above min_score.

        Returns an empty list when no results meet the threshold or when the
        underlying search fails gracefully.
        """
        namespace = config.namespace or str(config.index_id)
        try:
            raw = await self._store.search(
                vector=query_vector,
                top_k=config.top_k,
                namespace=namespace,
                filter=config.filters,
            )
        except Exception as exc:
            logger.error("Vector store search failed: %s", exc)
            return []

        results: list[RetrievalResult] = []
        for hit in raw:
            if hit.score < config.min_score:
                continue
            meta = hit.metadata or {}
            results.append(
                RetrievalResult(
                    chunk_id=hit.id,
                    document_id=meta.get("document_id", ""),
                    workspace_id=meta.get("workspace_id", ""),
                    text=meta.get("text", ""),
                    score=hit.score,
                    chunk_index=int(meta.get("chunk_index", 0)),
                    section_path=meta.get("section_path") or None,
                    metadata=meta,
                )
            )

        logger.info(
            "retrieve: index=%s top_k=%d returned=%d",
            config.index_id,
            config.top_k,
            len(results),
        )
        return results
