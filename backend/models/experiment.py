"""Experiment ORM model."""

import uuid
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from sqlalchemy import ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from backend.models.index import VectorIndex
    from backend.models.run import Run


class Experiment(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "experiments"

    workspace_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
    )
    index_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("indexes.id", ondelete="SET NULL"),
        nullable=True,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    experiment_config: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        "config", JSONB, nullable=True
    )
    config_hash: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)

    index: Mapped[Optional["VectorIndex"]] = relationship(
        "VectorIndex",
        back_populates="experiments",
        lazy="select",
    )
    runs: Mapped[List["Run"]] = relationship(
        "Run",
        back_populates="experiment",
        cascade="all, delete-orphan",
        lazy="select",
    )

    __table_args__ = (
        Index("ix_experiments_workspace_id", "workspace_id"),
        Index("ix_experiments_index_id", "index_id"),
    )

    def __repr__(self) -> str:
        return f"<Experiment id={self.id} name={self.name!r}>"
