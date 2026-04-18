"""Source citation formatting and document traceability for RAG responses."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class Citation:
    """A traceable reference from a response back to a source document."""

    chunk_id: str
    document_id: str
    score: float
    text_excerpt: str
    section_path: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def short_excerpt(self) -> str:
        """First 200 chars for inline display."""
        return self.text_excerpt[:200] + ("…" if len(self.text_excerpt) > 200 else "")


def build_citations(retrieval_results) -> List[Citation]:
    """Convert retrieval results into Citation objects.

    Accepts any objects with the attributes chunk_id, document_id, score,
    text, section_path, and metadata (compatible with RetrievalResult).
    """
    return [
        Citation(
            chunk_id=r.chunk_id,
            document_id=r.document_id,
            score=r.score,
            text_excerpt=r.text,
            section_path=r.section_path,
            metadata=r.metadata if hasattr(r, "metadata") else {},
        )
        for r in retrieval_results
    ]


def format_citations_markdown(citations: List[Citation]) -> str:
    """Render citations as a Markdown reference list."""
    if not citations:
        return ""
    lines = ["\n\n**Sources:**"]
    for i, c in enumerate(citations, 1):
        path = f" ({c.section_path})" if c.section_path else ""
        lines.append(f"{i}. `{c.document_id}`{path} — score {c.score:.3f}")
    return "\n".join(lines)


def annotate_answer(answer: str, citations: List[Citation]) -> str:
    """Append a citation block to the answer text."""
    return answer + format_citations_markdown(citations)
