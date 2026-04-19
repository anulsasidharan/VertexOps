"""Repository for Run aggregate."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.run import Run
from backend.repositories.base import BaseRepository


class RunRepository(BaseRepository[Run]):
    model = Run

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def list_by_experiment(self, experiment_id: UUID) -> list[Run]:
        result = await self.session.execute(select(Run).where(Run.experiment_id == experiment_id))
        return list(result.scalars().all())

    async def list_by_status(self, status: str) -> list[Run]:
        result = await self.session.execute(select(Run).where(Run.status == status))
        return list(result.scalars().all())
