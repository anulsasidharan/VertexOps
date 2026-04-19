"""Base types and interface for vector store providers."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class VectorRecord:
    """A single vector to upsert into the store."""

    id: str
    vector: list[float]
    metadata: dict[str, Any] = field(default_factory=dict)
    namespace: Optional[str] = None


@dataclass
class SearchResult:
    """A single result returned from a similarity search."""

    id: str
    score: float
    metadata: dict[str, Any] = field(default_factory=dict)


class BaseVectorStore(ABC):
    """Provider-agnostic interface for vector store operations."""

    @abstractmethod
    async def upsert(self, records: list[VectorRecord]) -> int:
        """Upsert records; return the number successfully stored."""
        ...

    @abstractmethod
    async def search(
        self,
        vector: list[float],
        top_k: int = 10,
        namespace: Optional[str] = None,
        filter: Optional[dict[str, Any]] = None,
    ) -> list[SearchResult]:
        """Return top_k nearest neighbours for *vector*."""
        ...

    @abstractmethod
    async def delete(self, ids: list[str], namespace: Optional[str] = None) -> None:
        """Delete vectors by ID."""
        ...

    @abstractmethod
    async def delete_namespace(self, namespace: str) -> None:
        """Delete all vectors in a namespace."""
        ...
