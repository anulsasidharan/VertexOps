"""Repository for Experiment aggregate."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.experiment import Experiment
from backend.repositories.base import BaseRepository


class ExperimentRepository(BaseRepository[Experiment]):
    model = Experiment

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def list_by_workspace(self, workspace_id: UUID) -> list[Experiment]:
        result = await self.session.execute(
            select(Experiment).where(Experiment.workspace_id == workspace_id)
        )
        return list(result.scalars().all())

    async def list_by_index(self, index_id: UUID) -> list[Experiment]:
        result = await self.session.execute(
            select(Experiment).where(Experiment.index_id == index_id)
        )
        return list(result.scalars().all())
