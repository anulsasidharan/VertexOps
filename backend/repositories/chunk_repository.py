"""Repository for Chunk aggregate."""

from typing import List
from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.chunk import Chunk
from backend.repositories.base import BaseRepository


class ChunkRepository(BaseRepository[Chunk]):
    model = Chunk

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def list_by_document(self, document_id: UUID) -> List[Chunk]:
        result = await self.session.execute(
            select(Chunk)
            .where(Chunk.document_id == document_id)
            .order_by(Chunk.chunk_index)
        )
        return list(result.scalars().all())

    async def delete_by_document(self, document_id: UUID) -> int:
        """Bulk-delete all chunks for a document; returns row count."""
        result = await self.session.execute(
            delete(Chunk).where(Chunk.document_id == document_id)
        )
        await self.session.flush()
        return result.rowcount
