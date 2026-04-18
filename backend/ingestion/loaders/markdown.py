"""Markdown document loader."""

import re
from typing import Optional

from backend.ingestion.loaders.base import BaseLoader, ParsedDocument

_H1_RE = re.compile(r"^#{1,2}\s+(.+)", re.MULTILINE)


class MarkdownLoader(BaseLoader):
    def load(self, content: bytes, filename: str) -> ParsedDocument:
        try:
            text = content.decode("utf-8")
        except UnicodeDecodeError:
            text = content.decode("latin-1")

        title: Optional[str] = None
        match = _H1_RE.search(text)
        if match:
            title = match.group(1).strip()[:200]

        return ParsedDocument(text=text, format="markdown", title=title)
