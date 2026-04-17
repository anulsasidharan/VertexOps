"""Repository for Document aggregate."""

from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.document import Document
from backend.repositories.base import BaseRepository


class DocumentRepository(BaseRepository[Document]):
    model = Document

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def get_by_content_hash(self, content_hash: str) -> Optional[Document]:
        result = await self.session.execute(
            select(Document).where(Document.content_hash == content_hash)
        )
        return result.scalars().first()

    async def list_by_workspace(self, workspace_id: UUID) -> List[Document]:
        result = await self.session.execute(
            select(Document).where(Document.workspace_id == workspace_id)
        )
        return list(result.scalars().all())

    async def list_by_status(self, ingest_status: str) -> List[Document]:
        result = await self.session.execute(
            select(Document).where(Document.ingest_status == ingest_status)
        )
        return list(result.scalars().all())

    async def list_by_workspace_and_status(
        self, workspace_id: UUID, ingest_status: str
    ) -> List[Document]:
        result = await self.session.execute(
            select(Document).where(
                Document.workspace_id == workspace_id,
                Document.ingest_status == ingest_status,
            )
        )
        return list(result.scalars().all())
