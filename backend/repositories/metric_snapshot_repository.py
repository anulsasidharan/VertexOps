"""Repository for MetricSnapshot aggregate."""

from typing import List
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.metric_snapshot import MetricSnapshot
from backend.repositories.base import BaseRepository


class MetricSnapshotRepository(BaseRepository[MetricSnapshot]):
    model = MetricSnapshot

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def list_by_run(self, run_id: UUID) -> List[MetricSnapshot]:
        result = await self.session.execute(
            select(MetricSnapshot).where(MetricSnapshot.run_id == run_id)
        )
        return list(result.scalars().all())
