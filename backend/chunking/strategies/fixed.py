"""Fixed-size chunking with configurable overlap."""

from backend.chunking.base import BaseChunker, ChunkResult


class FixedSizeChunker(BaseChunker):
    def __init__(self, chunk_size: int = 512, chunk_overlap: int = 64) -> None:
        if chunk_overlap >= chunk_size:
            raise ValueError("chunk_overlap must be less than chunk_size")
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk(self, text: str) -> list[ChunkResult]:
        if not text.strip():
            return []

        results: list[ChunkResult] = []
        start = 0
        idx = 0

        while start < len(text):
            end = min(start + self.chunk_size, len(text))
            chunk_text = text[start:end]
            if chunk_text.strip():
                results.append(
                    ChunkResult(
                        text=chunk_text,
                        chunk_index=idx,
                        start_char=start,
                        end_char=end,
                        token_count=self._estimate_tokens(chunk_text),
                    )
                )
                idx += 1
            if end == len(text):
                break
            start = end - self.chunk_overlap

        return results
