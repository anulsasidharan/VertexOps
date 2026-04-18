"""Plain-text document loader."""

from typing import Optional

from backend.ingestion.loaders.base import BaseLoader, ParsedDocument


class TxtLoader(BaseLoader):
    def load(self, content: bytes, filename: str) -> ParsedDocument:
        try:
            text = content.decode("utf-8")
        except UnicodeDecodeError:
            text = content.decode("latin-1")

        title: Optional[str] = None
        for line in text.splitlines():
            stripped = line.strip()
            if stripped:
                title = stripped[:200]
                break

        return ParsedDocument(text=text, format="txt", title=title)
