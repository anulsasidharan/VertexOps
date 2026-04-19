"""CSV document loader."""

import csv
import io
from typing import Optional

from backend.ingestion.loaders.base import BaseLoader, ParsedDocument


class CsvLoader(BaseLoader):
    def load(self, content: bytes, filename: str) -> ParsedDocument:
        try:
            raw = content.decode("utf-8")
        except UnicodeDecodeError:
            raw = content.decode("latin-1")

        reader = csv.reader(io.StringIO(raw))
        rows = list(reader)

        title: Optional[str] = None
        if rows and rows[0]:
            # Use header row as title hint if it looks like column names
            title = " | ".join(cell.strip() for cell in rows[0] if cell.strip())[:200] or None

        text = "\n".join(", ".join(cell for cell in row) for row in rows)

        return ParsedDocument(text=text, format="csv", title=title)
