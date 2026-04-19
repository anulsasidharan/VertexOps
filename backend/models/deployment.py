"""Deployment ORM model."""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import DateTime, ForeignKey, Index, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.models.base import Base, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from backend.models.index import VectorIndex


class Deployment(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "deployments"

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
    environment: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    revision: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="pending")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    index: Mapped[Optional["VectorIndex"]] = relationship(
        "VectorIndex",
        back_populates="deployments",
        lazy="select",
    )

    __table_args__ = (
        Index("ix_deployments_workspace_id", "workspace_id"),
        Index("ix_deployments_status", "status"),
    )

    def __repr__(self) -> str:
        return f"<Deployment id={self.id} env={self.environment!r} status={self.status!r}>"
