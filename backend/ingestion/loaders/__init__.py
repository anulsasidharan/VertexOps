"""Document loaders — format-specific parsers returning ParsedDocument."""

from backend.ingestion.loaders.base import BaseLoader, ParsedDocument
from backend.ingestion.loaders.registry import get_loader

__all__ = ["BaseLoader", "ParsedDocument", "get_loader"]
