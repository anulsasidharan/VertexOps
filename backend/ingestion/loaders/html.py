"""HTML document loader — strips tags using stdlib html.parser."""

from html.parser import HTMLParser
from typing import Optional

from backend.ingestion.loaders.base import BaseLoader, ParsedDocument


class _TextExtractor(HTMLParser):
    _SKIP_TAGS = frozenset({"script", "style", "head"})

    def __init__(self) -> None:
        super().__init__()
        self._parts: list[str] = []
        self._skip_depth: int = 0
        self.title: Optional[str] = None
        self._in_title: bool = False

    def handle_starttag(self, tag: str, attrs: list) -> None:
        if tag in self._SKIP_TAGS:
            self._skip_depth += 1
        if tag == "title":
            self._in_title = True

    def handle_endtag(self, tag: str) -> None:
        if tag in self._SKIP_TAGS:
            self._skip_depth = max(0, self._skip_depth - 1)
        if tag == "title":
            self._in_title = False

    def handle_data(self, data: str) -> None:
        if self._in_title:
            self.title = data.strip()[:200]
        if self._skip_depth == 0 and data.strip():
            self._parts.append(data)

    @property
    def text(self) -> str:
        return " ".join(self._parts)


class HtmlLoader(BaseLoader):
    def load(self, content: bytes, filename: str) -> ParsedDocument:
        try:
            raw = content.decode("utf-8")
        except UnicodeDecodeError:
            raw = content.decode("latin-1")

        extractor = _TextExtractor()
        extractor.feed(raw)

        return ParsedDocument(
            text=extractor.text,
            format="html",
            title=extractor.title,
        )
