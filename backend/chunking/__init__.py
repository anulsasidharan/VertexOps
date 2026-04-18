"""Chunking domain — strategy registry."""

from backend.chunking.base import BaseChunker, ChunkResult
from backend.chunking.registry import ChunkingConfig, get_chunker
from backend.chunking.service import ChunkingService

__all__ = ["BaseChunker", "ChunkResult", "ChunkingConfig", "ChunkingService", "get_chunker"]
