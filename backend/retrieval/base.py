"""Core types for the retrieval layer."""

from dataclasses import dataclass, field
from typing import Any, Optional
from uuid import UUID


@dataclass
class RetrievalResult:
    """A single retrieved chunk with source metadata for citation."""

    chunk_id: str
    document_id: str
    workspace_id: str
    text: str
    score: float
    chunk_index: int = 0
    section_path: Optional[str] = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class RetrievalConfig:
    """Parameters controlling a single retrieval call."""

    index_id: UUID
    top_k: int = 5
    min_score: float = 0.0
    namespace: Optional[str] = None
    filters: Optional[dict[str, Any]] = None
