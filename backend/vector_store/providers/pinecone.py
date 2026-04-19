"""Pinecone vector store adapter."""

import asyncio
from typing import Any, Optional

from backend.vector_store.base import BaseVectorStore, SearchResult, VectorRecord

_PINECONE_AVAILABLE: Optional[bool] = None


def _require_pinecone():
    global _PINECONE_AVAILABLE
    try:
        from pinecone import Pinecone  # noqa: F401

        _PINECONE_AVAILABLE = True
        return Pinecone
    except ImportError:
        _PINECONE_AVAILABLE = False
        raise ImportError("pinecone-client is required: pip install pinecone-client")


class PineconeVectorStore(BaseVectorStore):
    """Namespace-aware Pinecone adapter.

    The Pinecone SDK is synchronous; all operations are run in a thread pool
    via asyncio.to_thread to avoid blocking the event loop.
    """

    def __init__(self, api_key: str, index_name: str) -> None:
        self._api_key = api_key
        self._index_name = index_name
        self._client: Optional[object] = None
        self._index: Optional[object] = None

    def _get_index(self):
        if self._index is None:
            Pinecone = _require_pinecone()
            self._client = Pinecone(api_key=self._api_key)
            self._index = self._client.Index(self._index_name)
        return self._index

    async def upsert(self, records: list[VectorRecord]) -> int:
        if not records:
            return 0
        index = self._get_index()
        vectors = [
            {
                "id": r.id,
                "values": r.vector,
                "metadata": r.metadata,
            }
            for r in records
        ]
        namespace = records[0].namespace or ""

        def _do_upsert():
            index.upsert(vectors=vectors, namespace=namespace)

        await asyncio.to_thread(_do_upsert)
        return len(records)

    async def search(
        self,
        vector: list[float],
        top_k: int = 10,
        namespace: Optional[str] = None,
        filter: Optional[dict[str, Any]] = None,
    ) -> list[SearchResult]:
        index = self._get_index()

        def _do_query():
            kwargs: dict[str, Any] = {
                "vector": vector,
                "top_k": top_k,
                "include_metadata": True,
                "namespace": namespace or "",
            }
            if filter:
                kwargs["filter"] = filter
            return index.query(**kwargs)

        response = await asyncio.to_thread(_do_query)
        return [
            SearchResult(
                id=match["id"],
                score=match["score"],
                metadata=match.get("metadata") or {},
            )
            for match in response.get("matches", [])
        ]

    async def delete(self, ids: list[str], namespace: Optional[str] = None) -> None:
        if not ids:
            return
        index = self._get_index()

        def _do_delete():
            index.delete(ids=ids, namespace=namespace or "")

        await asyncio.to_thread(_do_delete)

    async def delete_namespace(self, namespace: str) -> None:
        index = self._get_index()

        def _do_delete_ns():
            index.delete(delete_all=True, namespace=namespace)

        await asyncio.to_thread(_do_delete_ns)
