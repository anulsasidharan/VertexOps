"""Prompt template registry for generation."""

from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class PromptTemplate:
    name: str
    system: str
    user_template: str  # Uses {context} and {question} placeholders

    def render(self, context: str, question: str) -> str:
        return self.user_template.format(context=context, question=question)


_REGISTRY: Dict[str, PromptTemplate] = {}


def register_template(template: PromptTemplate) -> None:
    _REGISTRY[template.name] = template


def get_template(name: str) -> PromptTemplate:
    if name not in _REGISTRY:
        raise KeyError(f"Prompt template '{name}' not found. Available: {list(_REGISTRY)}")
    return _REGISTRY[name]


def list_templates() -> List[str]:
    return list(_REGISTRY)


# Built-in templates

register_template(PromptTemplate(
    name="rag_default",
    system=(
        "You are a helpful AI assistant. Answer the user's question using only "
        "the provided context. If the context does not contain enough information "
        "to answer, say so clearly."
    ),
    user_template=(
        "Context:\n{context}\n\nQuestion: {question}\n\nAnswer:"
    ),
))

register_template(PromptTemplate(
    name="rag_concise",
    system=(
        "You are a concise AI assistant. Answer in 1-3 sentences using only "
        "the provided context. Be direct and factual."
    ),
    user_template=(
        "Context:\n{context}\n\nQuestion: {question}\n\nBrief answer:"
    ),
))

register_template(PromptTemplate(
    name="rag_technical",
    system=(
        "You are a technical AI assistant. Provide detailed, accurate answers "
        "with code examples where relevant. Use only the provided context."
    ),
    user_template=(
        "Technical context:\n{context}\n\nTechnical question: {question}\n\nDetailed answer:"
    ),
))
