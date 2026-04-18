"""Content hashing for deduplication."""

import hashlib


def compute_content_hash(content: bytes) -> str:
    """Return the SHA-256 hex digest of *content*."""
    return hashlib.sha256(content).hexdigest()
