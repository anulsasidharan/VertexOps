"""Repository for VectorIndex aggregate."""

from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.index import VectorIndex
from backend.repositories.base import BaseRepository


class IndexRepository(BaseRepository[VectorIndex]):
    model = VectorIndex

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def list_by_workspace(self, workspace_id: UUID) -> list[VectorIndex]:
        result = await self.session.execute(
            select(VectorIndex).where(VectorIndex.workspace_id == workspace_id)
        )
        return list(result.scalars().all())

    async def list_by_status(self, status: str) -> list[VectorIndex]:
        result = await self.session.execute(select(VectorIndex).where(VectorIndex.status == status))
        return list(result.scalars().all())

    async def get_by_config_hash(self, config_hash: str) -> Optional[VectorIndex]:
        result = await self.session.execute(
            select(VectorIndex).where(VectorIndex.config_hash == config_hash)
        )
        return result.scalars().first()
