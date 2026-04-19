"""OpenAI embedding adapter."""

from typing import Optional

from backend.embedding.base import BaseEmbeddingProvider, EmbeddingResult

_DIMENSIONS_MAP = {
    "text-embedding-3-small": 1536,
    "text-embedding-3-large": 3072,
    "text-embedding-ada-002": 1536,
}

_DEFAULT_BATCH_SIZE = 512


class OpenAIEmbeddingProvider(BaseEmbeddingProvider):
    """Embed texts using the OpenAI embeddings API.

    Lazy-initialises the AsyncOpenAI client on first use so the provider can
    be constructed without a live API key (useful in tests).
    """

    def __init__(
        self,
        api_key: str,
        model: str = "text-embedding-3-small",
        batch_size: int = _DEFAULT_BATCH_SIZE,
        max_retries: int = 3,
    ) -> None:
        self._api_key = api_key
        self._model = model
        self._batch_size = batch_size
        self._max_retries = max_retries
        self._client: Optional[object] = None

    @property
    def model_name(self) -> str:
        return self._model

    @property
    def dimensions(self) -> int:
        return _DIMENSIONS_MAP.get(self._model, 1536)

    def _get_client(self):
        if self._client is None:
            try:
                from openai import AsyncOpenAI
            except ImportError as exc:
                raise ImportError(
                    "openai package is required for OpenAIEmbeddingProvider: pip install openai"
                ) from exc
            self._client = AsyncOpenAI(api_key=self._api_key, max_retries=self._max_retries)
        return self._client

    async def embed(self, texts: list[str]) -> EmbeddingResult:
        if not texts:
            return EmbeddingResult(embeddings=[], model=self._model, dimensions=self.dimensions)

        client = self._get_client()
        all_embeddings: list[list[float]] = []
        total_tokens = 0

        for i in range(0, len(texts), self._batch_size):
            batch = texts[i : i + self._batch_size]
            response = await client.embeddings.create(model=self._model, input=batch)
            # sort by index to preserve order
            sorted_data = sorted(response.data, key=lambda d: d.index)
            all_embeddings.extend(d.embedding for d in sorted_data)
            if response.usage:
                total_tokens += response.usage.total_tokens

        return EmbeddingResult(
            embeddings=all_embeddings,
            model=self._model,
            dimensions=self.dimensions,
            token_usage=total_tokens,
        )
