"""MetricSnapshot ORM model."""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any, Optional

from sqlalchemy import DateTime, ForeignKey, Index, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.models.base import Base, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from backend.models.run import Run


class MetricSnapshot(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "metric_snapshots"

    run_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("runs.id", ondelete="CASCADE"),
        nullable=False,
    )
    snapshot_metrics: Mapped[Optional[dict[str, Any]]] = mapped_column(
        "metrics", JSONB, nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    run: Mapped["Run"] = relationship(
        "Run",
        back_populates="metric_snapshots",
        lazy="select",
    )

    __table_args__ = (Index("ix_metric_snapshots_run_id", "run_id"),)

    def __repr__(self) -> str:
        return f"<MetricSnapshot id={self.id} run_id={self.run_id}>"
