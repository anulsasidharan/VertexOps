"""Unit tests for embedding provider interface and OpenAI adapter."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from backend.embedding.base import BaseEmbeddingProvider, EmbeddingResult
from backend.embedding.service import EmbeddingService


# ---------------------------------------------------------------------------
# EmbeddingResult
# ---------------------------------------------------------------------------


def test_embedding_result_dimensions_inferred():
    result = EmbeddingResult(
        embeddings=[[0.1, 0.2, 0.3]], model="test-model", dimensions=0
    )
    assert result.dimensions == 3


def test_embedding_result_dimensions_explicit():
    result = EmbeddingResult(
        embeddings=[[0.1, 0.2]], model="test-model", dimensions=512
    )
    assert result.dimensions == 512


def test_embedding_result_empty_embeddings():
    result = EmbeddingResult(embeddings=[], model="test-model", dimensions=0)
    assert result.embeddings == []


def test_embedding_result_token_usage_default():
    result = EmbeddingResult(embeddings=[], model="m", dimensions=0)
    assert result.token_usage == 0


# ---------------------------------------------------------------------------
# BaseEmbeddingProvider is abstract
# ---------------------------------------------------------------------------


def test_base_provider_is_abstract():
    import inspect
    assert inspect.isabstract(BaseEmbeddingProvider)


# ---------------------------------------------------------------------------
# OpenAIEmbeddingProvider
# ---------------------------------------------------------------------------


def test_openai_provider_model_name():
    from backend.embedding.providers.openai import OpenAIEmbeddingProvider
    p = OpenAIEmbeddingProvider(api_key="sk-test", model="text-embedding-3-small")
    assert p.model_name == "text-embedding-3-small"


def test_openai_provider_dimensions_known_model():
    from backend.embedding.providers.openai import OpenAIEmbeddingProvider
    p = OpenAIEmbeddingProvider(api_key="sk-test", model="text-embedding-3-large")
    assert p.dimensions == 3072


def test_openai_provider_dimensions_unknown_model():
    from backend.embedding.providers.openai import OpenAIEmbeddingProvider
    p = OpenAIEmbeddingProvider(api_key="sk-test", model="custom-model")
    assert p.dimensions == 1536  # default


@pytest.mark.asyncio
async def test_openai_provider_embed_empty_returns_empty():
    from backend.embedding.providers.openai import OpenAIEmbeddingProvider
    p = OpenAIEmbeddingProvider(api_key="sk-test")
    result = await p.embed([])
    assert result.embeddings == []
    assert result.model == "text-embedding-3-small"


@pytest.mark.asyncio
async def test_openai_provider_embed_calls_api():
    from backend.embedding.providers.openai import OpenAIEmbeddingProvider

    mock_data = MagicMock()
    mock_data.index = 0
    mock_data.embedding = [0.1, 0.2, 0.3]

    mock_usage = MagicMock()
    mock_usage.total_tokens = 10

    mock_response = MagicMock()
    mock_response.data = [mock_data]
    mock_response.usage = mock_usage

    mock_client = AsyncMock()
    mock_client.embeddings.create = AsyncMock(return_value=mock_response)

    p = OpenAIEmbeddingProvider(api_key="sk-test", model="text-embedding-3-small")
    p._client = mock_client

    result = await p.embed(["hello world"])

    mock_client.embeddings.create.assert_awaited_once()
    assert result.embeddings == [[0.1, 0.2, 0.3]]
    assert result.token_usage == 10


@pytest.mark.asyncio
async def test_openai_provider_batches_large_input():
    from backend.embedding.providers.openai import OpenAIEmbeddingProvider

    calls = []

    def make_response(texts):
        data = [MagicMock(index=i, embedding=[float(i)]) for i in range(len(texts))]
        resp = MagicMock()
        resp.data = data
        resp.usage = MagicMock(total_tokens=len(texts))
        calls.append(len(texts))
        return resp

    mock_client = AsyncMock()
    mock_client.embeddings.create = AsyncMock(
        side_effect=lambda model, input: make_response(input)
    )

    p = OpenAIEmbeddingProvider(api_key="sk-test", batch_size=3)
    p._client = mock_client

    texts = ["t"] * 7  # 7 texts with batch_size=3 → 3 batches
    result = await p.embed(texts)

    assert len(result.embeddings) == 7
    assert len(calls) == 3  # ceil(7/3)


@pytest.mark.asyncio
async def test_openai_provider_preserves_order():
    from backend.embedding.providers.openai import OpenAIEmbeddingProvider

    # Return embeddings in reverse index order to test sorting
    def make_response(texts):
        data = [MagicMock(index=i, embedding=[float(i) * 0.1]) for i in range(len(texts))]
        data_reversed = list(reversed(data))
        resp = MagicMock()
        resp.data = data_reversed
        resp.usage = MagicMock(total_tokens=1)
        return resp

    mock_client = AsyncMock()
    mock_client.embeddings.create = AsyncMock(
        side_effect=lambda model, input: make_response(input)
    )

    p = OpenAIEmbeddingProvider(api_key="sk-test", batch_size=10)
    p._client = mock_client

    result = await p.embed(["a", "b", "c"])
    # embeddings should be [0.0, 0.1, 0.2] not reversed
    assert result.embeddings[0] == [0.0]
    assert result.embeddings[1] == [0.1]
    assert result.embeddings[2] == [0.2]


# ---------------------------------------------------------------------------
# EmbeddingService
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_service_embed_texts_delegates_to_provider():
    mock_provider = AsyncMock(spec=BaseEmbeddingProvider)
    mock_provider.embed = AsyncMock(
        return_value=EmbeddingResult(
            embeddings=[[0.1, 0.2]], model="m", dimensions=2
        )
    )
    mock_provider.model_name = "m"
    mock_provider.dimensions = 2

    svc = EmbeddingService(provider=mock_provider)
    result = await svc.embed_texts(["hello"])

    mock_provider.embed.assert_awaited_once_with(["hello"])
    assert result.embeddings == [[0.1, 0.2]]


@pytest.mark.asyncio
async def test_service_embed_single_returns_vector():
    mock_provider = AsyncMock(spec=BaseEmbeddingProvider)
    mock_provider.embed = AsyncMock(
        return_value=EmbeddingResult(
            embeddings=[[0.5, 0.6, 0.7]], model="m", dimensions=3
        )
    )
    mock_provider.model_name = "m"
    mock_provider.dimensions = 3

    svc = EmbeddingService(provider=mock_provider)
    vec = await svc.embed_single("test")
    assert vec == [0.5, 0.6, 0.7]


def test_service_exposes_model_name():
    mock_provider = MagicMock(spec=BaseEmbeddingProvider)
    mock_provider.model_name = "text-embedding-3-small"
    svc = EmbeddingService(provider=mock_provider)
    assert svc.model_name == "text-embedding-3-small"


def test_service_exposes_dimensions():
    mock_provider = MagicMock(spec=BaseEmbeddingProvider)
    mock_provider.dimensions = 1536
    svc = EmbeddingService(provider=mock_provider)
    assert svc.dimensions == 1536
