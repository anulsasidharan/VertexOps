"""Index ORM model."""

import uuid
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from sqlalchemy import ForeignKey, Index, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from backend.models.experiment import Experiment
    from backend.models.deployment import Deployment


class VectorIndex(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "indexes"

    workspace_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    vector_backend: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    namespace: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    config_hash: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    index_config: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        "config", JSONB, nullable=True
    )
    status: Mapped[str] = mapped_column(
        String(32), nullable=False, default="building"
    )

    experiments: Mapped[List["Experiment"]] = relationship(
        "Experiment",
        back_populates="index",
        lazy="select",
    )
    deployments: Mapped[List["Deployment"]] = relationship(
        "Deployment",
        back_populates="index",
        lazy="select",
    )

    __table_args__ = (
        Index("ix_indexes_workspace_id", "workspace_id"),
        Index("ix_indexes_status", "status"),
    )

    def __repr__(self) -> str:
        return f"<VectorIndex id={self.id} name={self.name!r} status={self.status!r}>"
