"""Base types for chunking strategies."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional


@dataclass
class ChunkResult:
    """A single text chunk with lineage metadata."""

    text: str
    chunk_index: int
    start_char: int
    end_char: int
    section_path: Optional[str] = None
    token_count: Optional[int] = None


class BaseChunker(ABC):
    """Split text into a sequence of ChunkResults."""

    @abstractmethod
    def chunk(self, text: str) -> list[ChunkResult]: ...

    @staticmethod
    def _estimate_tokens(text: str) -> int:
        return max(1, len(text) // 4)
