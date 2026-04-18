"""Vector store domain — index service and provider adapters."""

from backend.vector_store.base import BaseVectorStore, SearchResult, VectorRecord
from backend.vector_store.service import get_vector_store

__all__ = ["BaseVectorStore", "SearchResult", "VectorRecord", "get_vector_store"]
