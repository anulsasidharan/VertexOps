"""OpenAI chat completion adapter."""

import logging
from typing import Optional

from backend.generation.base import GenerationRequest, GenerationResponse

logger = logging.getLogger(__name__)

_CHARS_PER_TOKEN = 4  # rough estimate for token budgeting


class OpenAIChatProvider:
    """Wraps the OpenAI AsyncClient for chat completions."""

    def __init__(
        self,
        api_key: str,
        model: str = "gpt-4o-mini",
        max_retries: int = 3,
    ) -> None:
        self._api_key = api_key
        self._model = model
        self._max_retries = max_retries
        self._client = None  # lazy init

    def _get_client(self):
        if self._client is None:
            from openai import AsyncOpenAI
            self._client = AsyncOpenAI(
                api_key=self._api_key,
                max_retries=self._max_retries,
            )
        return self._client

    @property
    def model_name(self) -> str:
        return self._model

    async def complete(
        self,
        system_prompt: str,
        user_message: str,
        max_tokens: int = 1024,
        temperature: float = 0.2,
    ) -> GenerationResponse:
        """Call the OpenAI chat API and return a GenerationResponse."""
        client = self._get_client()
        try:
            response = await client.chat.completions.create(
                model=self._model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message},
                ],
                max_tokens=max_tokens,
                temperature=temperature,
            )
        except Exception as exc:
            logger.error("OpenAI completion failed: %s", exc)
            raise

        choice = response.choices[0]
        usage = response.usage
        return GenerationResponse(
            answer=choice.message.content or "",
            model=response.model,
            prompt_tokens=usage.prompt_tokens if usage else 0,
            completion_tokens=usage.completion_tokens if usage else 0,
            total_tokens=usage.total_tokens if usage else 0,
            finish_reason=choice.finish_reason or "stop",
        )
