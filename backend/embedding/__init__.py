"""Embedding domain — provider adapters."""

from backend.embedding.base import BaseEmbeddingProvider, EmbeddingResult
from backend.embedding.service import EmbeddingService

__all__ = ["BaseEmbeddingProvider", "EmbeddingResult", "EmbeddingService"]
