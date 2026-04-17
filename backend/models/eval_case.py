"""EvalCase ORM model."""

import uuid
from typing import TYPE_CHECKING, Any, Dict, Optional

from sqlalchemy import ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.models.base import Base, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from backend.models.run import Run


class EvalCase(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "eval_cases"

    run_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("runs.id", ondelete="CASCADE"),
        nullable=False,
    )
    question: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    ground_truth: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    predicted: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    case_metrics: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        "metrics", JSONB, nullable=True
    )
    failure_type: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)

    run: Mapped["Run"] = relationship(
        "Run",
        back_populates="eval_cases",
        lazy="select",
    )

    __table_args__ = (Index("ix_eval_cases_run_id", "run_id"),)

    def __repr__(self) -> str:
        return f"<EvalCase id={self.id} failure_type={self.failure_type!r}>"
