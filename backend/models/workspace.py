"""Workspace ORM model."""

from typing import TYPE_CHECKING, List

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from backend.models.user import User


class Workspace(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "workspaces"

    name: Mapped[str] = mapped_column(String(255), nullable=False)

    users: Mapped[List["User"]] = relationship(
        "User", back_populates="workspace", lazy="select"
    )

    def __repr__(self) -> str:
        return f"<Workspace id={self.id} name={self.name!r}>"
