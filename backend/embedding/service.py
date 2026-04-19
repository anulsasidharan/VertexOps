"""Embedding service — provider-agnostic batch embedding with rate-limit hooks."""

from typing import Optional

from backend.core.config import get_settings
from backend.embedding.base import BaseEmbeddingProvider, EmbeddingResult


def _build_default_provider() -> BaseEmbeddingProvider:
    settings = get_settings()
    if settings.openai_api_key:
        from backend.embedding.providers.openai import OpenAIEmbeddingProvider

        return OpenAIEmbeddingProvider(
            api_key=settings.openai_api_key.get_secret_value(),
            model=settings.openai_embedding_model,
            max_retries=settings.openai_max_retries,
        )
    raise RuntimeError("No embedding provider configured. Set OPENAI_API_KEY or GCP_PROJECT_ID.")


class EmbeddingService:
    """Wraps a BaseEmbeddingProvider with batch chunking and metadata passthrough."""

    def __init__(self, provider: Optional[BaseEmbeddingProvider] = None) -> None:
        self._provider = provider

    def _get_provider(self) -> BaseEmbeddingProvider:
        if self._provider is None:
            self._provider = _build_default_provider()
        return self._provider

    async def embed_texts(self, texts: list[str]) -> EmbeddingResult:
        """Embed a list of texts, returning all vectors in one EmbeddingResult."""
        return await self._get_provider().embed(texts)

    async def embed_single(self, text: str) -> list[float]:
        """Convenience wrapper — embed one text and return the vector."""
        result = await self._get_provider().embed([text])
        return result.embeddings[0]

    @property
    def model_name(self) -> str:
        return self._get_provider().model_name

    @property
    def dimensions(self) -> int:
        return self._get_provider().dimensions
