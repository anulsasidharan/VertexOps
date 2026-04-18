"""Chunking service — converts parsed text into Chunk model instances."""

import uuid
from typing import List

from backend.chunking.registry import ChunkingConfig, get_chunker
from backend.models.chunk import Chunk


class ChunkingService:
    """Chunk document text and produce unsaved Chunk ORM instances."""

    def chunk_document(
        self,
        document_id: uuid.UUID,
        text: str,
        config: ChunkingConfig,
    ) -> List[Chunk]:
        """Return a list of Chunk instances ready to be added to a session.

        Empty chunks (whitespace-only) are filtered out.
        """
        chunker = get_chunker(config)
        results = chunker.chunk(text)
        return [
            Chunk(
                document_id=document_id,
                chunk_index=r.chunk_index,
                text=r.text,
                token_count=r.token_count,
                section_path=r.section_path,
            )
            for r in results
            if r.text.strip()
        ]
