"""Repository for EvalCase aggregate."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.eval_case import EvalCase
from backend.repositories.base import BaseRepository


class EvalCaseRepository(BaseRepository[EvalCase]):
    model = EvalCase

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def list_by_run(self, run_id: UUID) -> list[EvalCase]:
        result = await self.session.execute(select(EvalCase).where(EvalCase.run_id == run_id))
        return list(result.scalars().all())

    async def list_by_failure_type(self, run_id: UUID, failure_type: str) -> list[EvalCase]:
        result = await self.session.execute(
            select(EvalCase).where(
                EvalCase.run_id == run_id,
                EvalCase.failure_type == failure_type,
            )
        )
        return list(result.scalars().all())
