"""Base types for document loaders."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional


@dataclass
class ParsedDocument:
    """Extracted content and metadata from a raw document."""

    text: str
    format: str
    title: Optional[str] = None
    language: Optional[str] = None
    page_count: Optional[int] = None

    @property
    def char_count(self) -> int:
        return len(self.text)


class BaseLoader(ABC):
    """Parse raw bytes into a ParsedDocument."""

    @abstractmethod
    def load(self, content: bytes, filename: str) -> ParsedDocument:
        ...
