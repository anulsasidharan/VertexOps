"""PDF document loader — requires pypdf (pip install pypdf)."""

import io
from typing import Optional

from backend.ingestion.loaders.base import BaseLoader, ParsedDocument

_PYPDF_AVAILABLE: Optional[bool] = None


def _require_pypdf():
    global _PYPDF_AVAILABLE
    try:
        import pypdf  # noqa: F401
        _PYPDF_AVAILABLE = True
        return pypdf
    except ImportError:
        _PYPDF_AVAILABLE = False
        raise ImportError(
            "pypdf is required for PDF parsing. Install it with: pip install pypdf"
        )


class PdfLoader(BaseLoader):
    def load(self, content: bytes, filename: str) -> ParsedDocument:
        pypdf = _require_pypdf()

        reader = pypdf.PdfReader(io.BytesIO(content))
        page_count = len(reader.pages)

        parts = []
        for page in reader.pages:
            page_text = page.extract_text() or ""
            if page_text.strip():
                parts.append(page_text)

        text = "\n\n".join(parts)

        # Try to extract title from PDF metadata
        title: Optional[str] = None
        if reader.metadata:
            raw_title = reader.metadata.get("/Title") or reader.metadata.get("title")
            if raw_title and str(raw_title).strip():
                title = str(raw_title).strip()[:200]

        return ParsedDocument(
            text=text,
            format="pdf",
            title=title,
            page_count=page_count,
        )
