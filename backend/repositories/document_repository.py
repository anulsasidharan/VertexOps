"""Repository for Document aggregate."""

from typing import Optional
from uuid import UUID

from sqlalchemy import func, select
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

    async def list_by_workspace(self, workspace_id: UUID) -> list[Document]:
        result = await self.session.execute(
            select(Document).where(Document.workspace_id == workspace_id)
        )
        return list(result.scalars().all())

    async def list_by_status(self, ingest_status: str) -> list[Document]:
        result = await self.session.execute(
            select(Document).where(Document.ingest_status == ingest_status)
        )
        return list(result.scalars().all())

    async def list_by_workspace_and_status(
        self, workspace_id: UUID, ingest_status: str
    ) -> list[Document]:
        result = await self.session.execute(
            select(Document).where(
                Document.workspace_id == workspace_id,
                Document.ingest_status == ingest_status,
            )
        )
        return list(result.scalars().all())

    async def count_by_workspace(self, workspace_id: UUID) -> int:
        result = await self.session.execute(
            select(func.count()).select_from(Document).where(Document.workspace_id == workspace_id)
        )
        return result.scalar_one()

    async def count_by_workspace_and_status(self, workspace_id: UUID, ingest_status: str) -> int:
        result = await self.session.execute(
            select(func.count())
            .select_from(Document)
            .where(
                Document.workspace_id == workspace_id,
                Document.ingest_status == ingest_status,
            )
        )
        return result.scalar_one()

    async def list_by_workspace_paginated(
        self, workspace_id: UUID, offset: int, limit: int
    ) -> list[Document]:
        result = await self.session.execute(
            select(Document)
            .where(Document.workspace_id == workspace_id)
            .order_by(Document.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def list_by_workspace_and_status_paginated(
        self, workspace_id: UUID, ingest_status: str, offset: int, limit: int
    ) -> list[Document]:
        result = await self.session.execute(
            select(Document)
            .where(
                Document.workspace_id == workspace_id,
                Document.ingest_status == ingest_status,
            )
            .order_by(Document.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        return list(result.scalars().all())
