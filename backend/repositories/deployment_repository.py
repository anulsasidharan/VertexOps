"""Repository for Deployment aggregate."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.deployment import Deployment
from backend.repositories.base import BaseRepository


class DeploymentRepository(BaseRepository[Deployment]):
    model = Deployment

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def list_by_workspace(self, workspace_id: UUID) -> list[Deployment]:
        result = await self.session.execute(
            select(Deployment).where(Deployment.workspace_id == workspace_id)
        )
        return list(result.scalars().all())

    async def list_by_status(self, status: str) -> list[Deployment]:
        result = await self.session.execute(select(Deployment).where(Deployment.status == status))
        return list(result.scalars().all())

    async def list_by_environment(self, workspace_id: UUID, environment: str) -> list[Deployment]:
        result = await self.session.execute(
            select(Deployment).where(
                Deployment.workspace_id == workspace_id,
                Deployment.environment == environment,
            )
        )
        return list(result.scalars().all())
