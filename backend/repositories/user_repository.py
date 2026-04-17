"""Repository for User aggregate."""

from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.user import User
from backend.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    model = User

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def get_by_email(self, email: str) -> Optional[User]:
        result = await self.session.execute(
            select(User).where(User.email == email)
        )
        return result.scalars().first()

    async def list_by_workspace(self, workspace_id: UUID) -> List[User]:
        result = await self.session.execute(
            select(User).where(User.workspace_id == workspace_id)
        )
        return list(result.scalars().all())
