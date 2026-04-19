"""Generic async repository base for SQLAlchemy 2.0."""

from typing import Generic, Optional, TypeVar
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.base import Base

ModelT = TypeVar("ModelT", bound=Base)


class BaseRepository(Generic[ModelT]):
    """Provides get / list / add / delete over an AsyncSession.

    Concrete repositories set ``model`` at the class level and inject a
    session via ``__init__``.  All mutations use ``flush`` so that the
    calling layer controls the commit boundary.
    """

    model: type[ModelT]

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get(self, id: UUID) -> Optional[ModelT]:
        return await self.session.get(self.model, id)

    async def list(self) -> list[ModelT]:
        result = await self.session.execute(select(self.model))
        return list(result.scalars().all())

    async def add(self, instance: ModelT) -> ModelT:
        self.session.add(instance)
        await self.session.flush()
        await self.session.refresh(instance)
        return instance

    async def delete(self, instance: ModelT) -> None:
        await self.session.delete(instance)
        await self.session.flush()
