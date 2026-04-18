"""Generation service — assembles context, applies token budgeting, calls provider."""

import logging
from typing import List, Optional

from backend.generation.base import GenerationRequest, GenerationResponse
from backend.generation.templates import get_template

logger = logging.getLogger(__name__)

_CHARS_PER_TOKEN = 4  # used for token budget estimation


class GenerationService:
    """Orchestrates prompt assembly and LLM invocation with token budgeting."""

    def __init__(self, provider=None) -> None:
        self._provider = provider or _build_default_provider()

    async def generate(self, request: GenerationRequest) -> GenerationResponse:
        """Assemble the prompt and call the underlying provider."""
        template = get_template(request.template_name)
        system = request.system_prompt or template.system

        context = self._build_context(
            request.context_chunks, request.max_tokens, system
        )
        user_message = template.render(context=context, question=request.question)

        try:
            return await self._provider.complete(
                system_prompt=system,
                user_message=user_message,
                max_tokens=request.max_tokens,
                temperature=request.temperature,
            )
        except Exception as exc:
            logger.error("Generation failed: %s", exc)
            raise

    def _build_context(
        self,
        chunks: List[str],
        max_tokens: int,
        system: str,
        reserved_answer_tokens: int = 256,
    ) -> str:
        """Join chunks while staying within a rough token budget.

        Reserves space for the system prompt and the model's answer so the
        total assembled prompt fits within max_tokens.
        """
        system_tokens = len(system) // _CHARS_PER_TOKEN
        budget = max_tokens - system_tokens - reserved_answer_tokens
        if budget <= 0:
            return ""

        parts: List[str] = []
        used = 0
        for chunk in chunks:
            chunk_tokens = len(chunk) // _CHARS_PER_TOKEN
            if used + chunk_tokens > budget:
                break
            parts.append(chunk)
            used += chunk_tokens

        return "\n\n".join(parts)


def _build_default_provider():
    from backend.core.config import get_settings
    settings = get_settings()
    if settings.openai_api_key:
        from backend.generation.providers.openai import OpenAIChatProvider
        return OpenAIChatProvider(
            api_key=settings.openai_api_key.get_secret_value(),
            model=settings.openai_chat_model,
            max_retries=settings.openai_max_retries,
        )
    raise RuntimeError(
        "No generation provider configured. Set OPENAI_API_KEY or configure a Vertex AI provider."
    )
