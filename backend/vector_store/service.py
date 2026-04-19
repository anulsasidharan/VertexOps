"""Vector store service — provider selection and singleton."""

from typing import Optional

from backend.vector_store.base import BaseVectorStore

_store: Optional[BaseVectorStore] = None


def get_vector_store() -> BaseVectorStore:
    """Return the singleton vector store, initialising it from settings on first call."""
    global _store
    if _store is None:
        _store = _create_store()
    return _store


def _create_store() -> BaseVectorStore:
    from backend.core.config import get_settings

    settings = get_settings()

    if settings.pinecone_api_key and settings.pinecone_index_name:
        from backend.vector_store.providers.pinecone import PineconeVectorStore

        return PineconeVectorStore(
            api_key=settings.pinecone_api_key.get_secret_value(),
            index_name=settings.pinecone_index_name,
        )

    raise RuntimeError("No vector store configured. Set PINECONE_API_KEY and PINECONE_INDEX_NAME.")
