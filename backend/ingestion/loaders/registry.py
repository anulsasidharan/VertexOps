"""Loader registry — maps file extensions and MIME types to loader classes."""

from pathlib import Path
from typing import Dict, Optional, Type

from backend.ingestion.loaders.base import BaseLoader
from backend.ingestion.loaders.csv import CsvLoader
from backend.ingestion.loaders.docx import DocxLoader
from backend.ingestion.loaders.html import HtmlLoader
from backend.ingestion.loaders.markdown import MarkdownLoader
from backend.ingestion.loaders.pdf import PdfLoader
from backend.ingestion.loaders.txt import TxtLoader

_EXTENSION_MAP: Dict[str, Type[BaseLoader]] = {
    ".txt": TxtLoader,
    ".md": MarkdownLoader,
    ".markdown": MarkdownLoader,
    ".html": HtmlLoader,
    ".htm": HtmlLoader,
    ".csv": CsvLoader,
    ".pdf": PdfLoader,
    ".docx": DocxLoader,
}

_MIME_MAP: Dict[str, Type[BaseLoader]] = {
    "text/plain": TxtLoader,
    "text/markdown": MarkdownLoader,
    "text/html": HtmlLoader,
    "text/csv": CsvLoader,
    "application/csv": CsvLoader,
    "application/pdf": PdfLoader,
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": DocxLoader,
}


def get_loader(filename: str, content_type: Optional[str] = None) -> BaseLoader:
    """Return the appropriate loader for *filename* or *content_type*.

    Extension takes precedence; MIME type is used as a fallback.
    Raises ValueError when no loader is found.
    """
    ext = Path(filename).suffix.lower()
    loader_cls = _EXTENSION_MAP.get(ext)

    if loader_cls is None and content_type:
        mime = content_type.split(";")[0].strip().lower()
        loader_cls = _MIME_MAP.get(mime)

    if loader_cls is None:
        raise ValueError(
            f"No loader available for filename={filename!r}, content_type={content_type!r}. "
            f"Supported extensions: {sorted(_EXTENSION_MAP)}"
        )

    return loader_cls()
