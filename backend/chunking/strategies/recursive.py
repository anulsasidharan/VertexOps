"""Recursive character text splitter — tries separators in order."""

from typing import Optional

from backend.chunking.base import BaseChunker, ChunkResult

_DEFAULT_SEPARATORS = ["\n\n", "\n", ". ", " ", ""]


class RecursiveChunker(BaseChunker):
    def __init__(
        self,
        chunk_size: int = 512,
        chunk_overlap: int = 64,
        separators: Optional[list[str]] = None,
    ) -> None:
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.separators = separators if separators is not None else _DEFAULT_SEPARATORS

    def chunk(self, text: str) -> list[ChunkResult]:
        if not text.strip():
            return []
        pieces = self._split_recursive(text, self.separators)
        return self._assign_positions(pieces, text)

    # ------------------------------------------------------------------

    def _split_recursive(self, text: str, separators: list[str]) -> list[str]:
        if len(text) <= self.chunk_size or not separators:
            return [text] if text.strip() else []

        sep, rest = separators[0], separators[1:]
        if sep:
            raw_pieces = text.split(sep)
        else:
            # Character-level fallback: fixed windows
            return [
                text[i : i + self.chunk_size]
                for i in range(0, len(text), self.chunk_size - self.chunk_overlap)
                if text[i : i + self.chunk_size].strip()
            ]

        expanded: list[str] = []
        for piece in raw_pieces:
            if not piece.strip():
                continue
            if len(piece) > self.chunk_size:
                expanded.extend(self._split_recursive(piece, rest))
            else:
                expanded.append(piece)

        return self._merge_pieces(expanded)

    def _merge_pieces(self, pieces: list[str]) -> list[str]:
        if not pieces:
            return []
        merged: list[str] = []
        current = pieces[0]
        for piece in pieces[1:]:
            joined = current + " " + piece
            if len(joined) <= self.chunk_size:
                current = joined
            else:
                merged.append(current)
                current = piece
        merged.append(current)
        return merged

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
