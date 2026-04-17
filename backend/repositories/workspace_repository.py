"""Repository for Workspace aggregate."""

from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.workspace import Workspace
from backend.repositories.base import BaseRepository


class WorkspaceRepository(BaseRepository[Workspace]):
    model = Workspace

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def get_by_name(self, name: str) -> Optional[Workspace]:
        result = await self.session.execute(
            select(Workspace).where(Workspace.name == name)
        )
        return result.scalars().first()
