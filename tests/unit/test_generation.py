"""Unit tests for generation service, templates, and OpenAI adapter."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from backend.generation.base import GenerationRequest, GenerationResponse
from backend.generation.service import GenerationService
from backend.generation.templates import (
    PromptTemplate,
    get_template,
    list_templates,
    register_template,
)

# ---------------------------------------------------------------------------
# PromptTemplate
# ---------------------------------------------------------------------------


def test_template_render():
    t = PromptTemplate(
        name="test", system="sys", user_template="Context:\n{context}\nQ: {question}"
    )
    rendered = t.render(context="ctx text", question="What?")
    assert "ctx text" in rendered
    assert "What?" in rendered


def test_builtin_rag_default_exists():
    t = get_template("rag_default")
    assert t.name == "rag_default"
    assert "{context}" in t.user_template
    assert "{question}" in t.user_template


def test_builtin_rag_concise_exists():
    t = get_template("rag_concise")
    assert "concise" in t.system.lower()


def test_builtin_rag_technical_exists():
    t = get_template("rag_technical")
    assert "technical" in t.system.lower()


def test_get_template_unknown_raises():
    with pytest.raises(KeyError, match="not found"):
        get_template("does_not_exist_xyz")


def test_list_templates_contains_builtins():
    names = list_templates()
    assert "rag_default" in names
    assert "rag_concise" in names
    assert "rag_technical" in names


def test_register_custom_template():
    register_template(
        PromptTemplate(name="custom_test", system="sys", user_template="{context} {question}")
    )
    assert "custom_test" in list_templates()


# ---------------------------------------------------------------------------
# GenerationService — context budgeting
# ---------------------------------------------------------------------------


def _make_svc(answer: str = "The answer.") -> tuple:
    provider = MagicMock()
    provider.complete = AsyncMock(
        return_value=GenerationResponse(
            answer=answer,
            model="gpt-4o-mini",
            prompt_tokens=10,
            completion_tokens=5,
            total_tokens=15,
        )
    )
    svc = GenerationService(provider=provider)
    return svc, provider


@pytest.mark.asyncio
async def test_generate_returns_response():
    svc, _ = _make_svc("42")
    req = GenerationRequest(question="What is the answer?", context_chunks=["context text"])
    resp = await svc.generate(req)
    assert resp.answer == "42"
    assert resp.model == "gpt-4o-mini"


@pytest.mark.asyncio
async def test_generate_passes_template_system():
    svc, provider = _make_svc()
    req = GenerationRequest(question="Q?", template_name="rag_concise")
    await svc.generate(req)
    call_kwargs = provider.complete.call_args[1]
    assert "concise" in call_kwargs["system_prompt"].lower()


@pytest.mark.asyncio
async def test_generate_custom_system_overrides_template():
    svc, provider = _make_svc()
    req = GenerationRequest(question="Q?", system_prompt="Custom sys prompt")
    await svc.generate(req)
    call_kwargs = provider.complete.call_args[1]
    assert call_kwargs["system_prompt"] == "Custom sys prompt"


@pytest.mark.asyncio
async def test_generate_context_assembled_in_user_message():
    svc, provider = _make_svc()
    req = GenerationRequest(question="Q?", context_chunks=["chunk one", "chunk two"])
    await svc.generate(req)
    call_kwargs = provider.complete.call_args[1]
    assert "chunk one" in call_kwargs["user_message"]
    assert "chunk two" in call_kwargs["user_message"]


@pytest.mark.asyncio
async def test_generate_token_budget_truncates_chunks():
    svc, provider = _make_svc()
    # Very small max_tokens — should truncate large context
    large_chunks = ["word " * 500 for _ in range(5)]
    req = GenerationRequest(question="Q?", context_chunks=large_chunks, max_tokens=64)
    await svc.generate(req)
    call_kwargs = provider.complete.call_args[1]
    # Assembled context should be much shorter than all 5 chunks combined
    assert len(call_kwargs["user_message"]) < len("word " * 500 * 5)


@pytest.mark.asyncio
async def test_generate_no_chunks_empty_context():
    svc, provider = _make_svc()
    req = GenerationRequest(question="Q?", context_chunks=[])
    await svc.generate(req)
    call_kwargs = provider.complete.call_args[1]
    assert "Q?" in call_kwargs["user_message"]


@pytest.mark.asyncio
async def test_generate_provider_error_propagates():
    provider = MagicMock()
    provider.complete = AsyncMock(side_effect=RuntimeError("API down"))
    svc = GenerationService(provider=provider)
    req = GenerationRequest(question="Q?")
    with pytest.raises(RuntimeError, match="API down"):
        await svc.generate(req)


# ---------------------------------------------------------------------------
# GenerationResponse helpers
# ---------------------------------------------------------------------------


def test_generation_response_total_cost_tokens():
    resp = GenerationResponse(
        answer="hi", model="m", prompt_tokens=100, completion_tokens=50, total_tokens=150
    )
    assert resp.total_cost_tokens == 150


# ---------------------------------------------------------------------------
# OpenAIChatProvider
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_openai_provider_calls_api():
    from backend.generation.providers.openai import OpenAIChatProvider

    mock_usage = MagicMock(prompt_tokens=10, completion_tokens=5, total_tokens=15)
    mock_choice = MagicMock()
    mock_choice.message.content = "Hello!"
    mock_choice.finish_reason = "stop"
    mock_response = MagicMock(choices=[mock_choice], model="gpt-4o-mini", usage=mock_usage)

    mock_client = MagicMock()
    mock_client.chat = MagicMock()
    mock_client.chat.completions = MagicMock()
    mock_client.chat.completions.create = AsyncMock(return_value=mock_response)

    provider = OpenAIChatProvider(api_key="test-key", model="gpt-4o-mini")
    provider._client = mock_client

    resp = await provider.complete(
        system_prompt="You are helpful.", user_message="Hi!", max_tokens=256
    )
    assert resp.answer == "Hello!"
    assert resp.model == "gpt-4o-mini"
    assert resp.prompt_tokens == 10


@pytest.mark.asyncio
async def test_openai_provider_error_propagates():
    from backend.generation.providers.openai import OpenAIChatProvider

    mock_client = MagicMock()
    mock_client.chat.completions.create = AsyncMock(side_effect=Exception("rate limit"))

    provider = OpenAIChatProvider(api_key="test-key")
    provider._client = mock_client

    with pytest.raises(Exception, match="rate limit"):
        await provider.complete("sys", "user")
