"""Repository for APIKey aggregate."""

from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.api_key import APIKey
from backend.repositories.base import BaseRepository


class APIKeyRepository(BaseRepository[APIKey]):
    model = APIKey

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def get_by_hash(self, key_hash: str) -> Optional[APIKey]:
        result = await self.session.execute(select(APIKey).where(APIKey.key_hash == key_hash))
        return result.scalars().first()

    async def list_by_user(self, user_id: UUID) -> list[APIKey]:
        result = await self.session.execute(select(APIKey).where(APIKey.user_id == user_id))
        return list(result.scalars().all())
