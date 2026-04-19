"""Chunking strategy registry — maps config to chunker instance."""

from dataclasses import dataclass
from typing import Literal, Optional

from backend.chunking.base import BaseChunker
from backend.chunking.strategies.code import CodeChunker
from backend.chunking.strategies.fixed import FixedSizeChunker
from backend.chunking.strategies.markdown import MarkdownChunker
from backend.chunking.strategies.recursive import RecursiveChunker

Strategy = Literal["fixed", "recursive", "markdown", "code"]


@dataclass
class ChunkingConfig:
    strategy: Strategy = "fixed"
    chunk_size: int = 512
    chunk_overlap: int = 64
    separators: Optional[list[str]] = None


def get_chunker(config: ChunkingConfig) -> BaseChunker:
    """Return the chunker for *config.strategy*.

    Raises ValueError for unknown strategies.
    """
    if config.strategy == "fixed":
        return FixedSizeChunker(config.chunk_size, config.chunk_overlap)
    if config.strategy == "recursive":
        return RecursiveChunker(config.chunk_size, config.chunk_overlap, config.separators)
    if config.strategy == "markdown":
        return MarkdownChunker(config.chunk_size, config.chunk_overlap)
    if config.strategy == "code":
        return CodeChunker(config.chunk_size, config.chunk_overlap)
    raise ValueError(
        f"Unknown chunking strategy: {config.strategy!r}. "
        f"Supported: 'fixed', 'recursive', 'markdown', 'code'"
    )
