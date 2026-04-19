"""Markdown-aware chunker — splits at heading boundaries first."""

import re

from backend.chunking.base import BaseChunker, ChunkResult
from backend.chunking.strategies.fixed import FixedSizeChunker

_HEADING_RE = re.compile(r"^(#{1,6})\s+(.+)$", re.MULTILINE)


class MarkdownChunker(BaseChunker):
    def __init__(self, chunk_size: int = 512, chunk_overlap: int = 64) -> None:
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self._fixed = FixedSizeChunker(chunk_size, chunk_overlap)

    def chunk(self, text: str) -> list[ChunkResult]:
        if not text.strip():
            return []

        sections = self._split_sections(text)
        results: list[ChunkResult] = []
        global_idx = 0
        global_offset = 0

        for section_path, section_text in sections:
            if not section_text.strip():
                continue
            if len(section_text) <= self.chunk_size:
                start = text.find(section_text, global_offset)
                start = start if start != -1 else global_offset
                end = start + len(section_text)
                results.append(
                    ChunkResult(
                        text=section_text,
                        chunk_index=global_idx,
                        start_char=start,
                        end_char=end,
                        section_path=section_path or None,
                        token_count=self._estimate_tokens(section_text),
                    )
                )
                global_idx += 1
                global_offset = max(0, end - self.chunk_overlap)
            else:
                for sub in self._fixed.chunk(section_text):
                    abs_start = text.find(sub.text, global_offset)
                    abs_start = abs_start if abs_start != -1 else global_offset
                    abs_end = abs_start + len(sub.text)
                    results.append(
                        ChunkResult(
                            text=sub.text,
                            chunk_index=global_idx,
                            start_char=abs_start,
                            end_char=abs_end,
                            section_path=section_path or None,
                            token_count=sub.token_count,
                        )
                    )
                    global_idx += 1
                    global_offset = max(0, abs_end - self.chunk_overlap)

        return results

    def _split_sections(self, text: str) -> list[tuple[str, str]]:
        """Return (heading_text, content) pairs split at heading boundaries."""
        sections: list[tuple[str, str]] = []
        current_heading = ""
        current_start = 0

        for m in _HEADING_RE.finditer(text):
            if current_start < m.start():
                content = text[current_start : m.start()].strip()
                if content:
                    sections.append((current_heading, content))
            current_heading = m.group(2).strip()
            current_start = m.end()

        tail = text[current_start:].strip()
        if tail:
            sections.append((current_heading, tail))

        return sections if sections else [("", text)]
