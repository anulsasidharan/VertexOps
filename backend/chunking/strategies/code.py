"""Code-aware chunker — splits at top-level definition boundaries."""

import re

from backend.chunking.base import BaseChunker, ChunkResult
from backend.chunking.strategies.fixed import FixedSizeChunker

# Top-level Python/JS/Go-style blocks separated by blank lines before a definition
_BLOCK_SEP_RE = re.compile(r"\n{2,}")


class CodeChunker(BaseChunker):
    def __init__(self, chunk_size: int = 512, chunk_overlap: int = 64) -> None:
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self._fixed = FixedSizeChunker(chunk_size, chunk_overlap)

    def chunk(self, text: str) -> list[ChunkResult]:
        if not text.strip():
            return []

        blocks = [b.strip() for b in _BLOCK_SEP_RE.split(text) if b.strip()]
        merged = self._merge_blocks(blocks)
        return self._assign_positions(merged, text)

    def _merge_blocks(self, blocks: list[str]) -> list[str]:
        result: list[str] = []
        current = ""
        for block in blocks:
            if len(block) > self.chunk_size:
                if current:
                    result.append(current)
                    current = ""
                # oversized block → fixed-size split
                for sub in self._fixed.chunk(block):
                    result.append(sub.text)
            elif current and len(current) + len(block) + 2 <= self.chunk_size:
                current = current + "\n\n" + block
            else:
                if current:
                    result.append(current)
                current = block
        if current:
            result.append(current)
        return result

    def _assign_positions(self, texts: list[str], original: str) -> list[ChunkResult]:
        results: list[ChunkResult] = []
        search_from = 0
        for idx, t in enumerate(texts):
            pos = original.find(t, search_from)
            start = pos if pos != -1 else search_from
            end = start + len(t)
            results.append(
                ChunkResult(
                    text=t,
                    chunk_index=idx,
                    start_char=start,
                    end_char=end,
                    token_count=self._estimate_tokens(t),
                )
            )
            search_from = max(0, end - self.chunk_overlap)
        return results
