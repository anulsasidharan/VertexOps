"""Base types and interface for embedding providers."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List


@dataclass
class EmbeddingResult:
    """Vectors returned from an embedding provider for a batch of texts."""

    embeddings: List[List[float]]
    model: str
    dimensions: int
    token_usage: int = 0

    def __post_init__(self) -> None:
        if self.dimensions == 0 and self.embeddings:
            self.dimensions = len(self.embeddings[0])


class BaseEmbeddingProvider(ABC):
    """Provider-agnostic interface for computing text embeddings."""

    @abstractmethod
    async def embed(self, texts: List[str]) -> EmbeddingResult:
        """Embed a batch of texts and return an EmbeddingResult."""
        ...

    @property
    @abstractmethod
    def model_name(self) -> str:
        """The model identifier used by this provider."""
        ...

    @property
    @abstractmethod
    def dimensions(self) -> int:
        """Vector dimensionality produced by this provider."""
        ...
