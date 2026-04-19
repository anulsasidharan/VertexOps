"""Core types for the generation layer."""

from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class GenerationRequest:
    """Input to the generation service."""

    question: str
    context_chunks: list[str] = field(default_factory=list)
    template_name: str = "rag_default"
    system_prompt: Optional[str] = None
    max_tokens: int = 1024
    temperature: float = 0.2
    extra: dict[str, Any] = field(default_factory=dict)


@dataclass
class GenerationResponse:
    """Output from the generation service."""

    answer: str
    model: str
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    finish_reason: str = "stop"

    @property
    def total_cost_tokens(self) -> int:
        return self.prompt_tokens + self.completion_tokens
