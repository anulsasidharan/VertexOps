"""Run ORM model."""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from sqlalchemy import DateTime, ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.models.base import Base, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from backend.models.experiment import Experiment
    from backend.models.eval_case import EvalCase
    from backend.models.metric_snapshot import MetricSnapshot


class Run(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "runs"

    experiment_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("experiments.id", ondelete="CASCADE"),
        nullable=False,
    )
    status: Mapped[str] = mapped_column(
        String(32), nullable=False, default="queued"
    )
    started_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    finished_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    artifact_uri: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    run_logs: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        "logs", JSONB, nullable=True
    )

    experiment: Mapped["Experiment"] = relationship(
        "Experiment",
        back_populates="runs",
        lazy="select",
    )
    eval_cases: Mapped[List["EvalCase"]] = relationship(
        "EvalCase",
        back_populates="run",
        cascade="all, delete-orphan",
        lazy="select",
    )
    metric_snapshots: Mapped[List["MetricSnapshot"]] = relationship(
        "MetricSnapshot",
        back_populates="run",
        cascade="all, delete-orphan",
        lazy="select",
    )

    __table_args__ = (
        Index("ix_runs_experiment_id", "experiment_id"),
        Index("ix_runs_status", "status"),
    )

    def __repr__(self) -> str:
        return f"<Run id={self.id} status={self.status!r}>"
