"""File upload validation — type and size guards."""

from pathlib import Path
from typing import Optional

from backend.core.exceptions import DomainValidationError

MAX_FILE_SIZE_BYTES: int = 50 * 1024 * 1024  # 50 MB

SUPPORTED_EXTENSIONS: frozenset = frozenset(
    {".txt", ".md", ".markdown", ".html", ".htm", ".csv", ".pdf", ".docx"}
)

SUPPORTED_MIME_TYPES: frozenset = frozenset(
    {
        "text/plain",
        "text/markdown",
        "text/html",
        "text/csv",
        "application/csv",
        "application/pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    }
)


def validate_file(
    filename: str,
    size_bytes: int,
    content_type: Optional[str] = None,
) -> None:
    """Raise DomainValidationError when the file cannot be accepted.

    Checks (in order):
    1. File size ≤ MAX_FILE_SIZE_BYTES
    2. Extension is in SUPPORTED_EXTENSIONS, *or* content_type is in SUPPORTED_MIME_TYPES
    """
    if size_bytes > MAX_FILE_SIZE_BYTES:
        raise DomainValidationError(
            f"File size {size_bytes:,} bytes exceeds the {MAX_FILE_SIZE_BYTES // (1024 * 1024)} MB limit.",
            details={"size_bytes": size_bytes, "max_bytes": MAX_FILE_SIZE_BYTES},
        )

    ext = Path(filename).suffix.lower()
    mime = (content_type or "").split(";")[0].strip().lower()

    if ext not in SUPPORTED_EXTENSIONS and mime not in SUPPORTED_MIME_TYPES:
        raise DomainValidationError(
            f"Unsupported file type: extension={ext!r}, content_type={content_type!r}. "
            f"Supported extensions: {sorted(SUPPORTED_EXTENSIONS)}",
            details={"extension": ext, "content_type": content_type},
        )
