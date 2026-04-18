"""Create indexes, experiments, runs, eval_cases, metric_snapshots, deployments tables.

Revision ID: 0003
Revises: 0002
Create Date: 2026-04-17

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB, UUID

revision: str = "0003"
down_revision: Union[str, None] = "0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # indexes
    op.create_table(
        "indexes",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "workspace_id",
            UUID(as_uuid=True),
            sa.ForeignKey("workspaces.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("vector_backend", sa.String(64), nullable=True),
        sa.Column("namespace", sa.String(255), nullable=True),
        sa.Column("config_hash", sa.String(128), nullable=True),
        sa.Column("config", JSONB, nullable=True),
        sa.Column("status", sa.String(32), nullable=False, server_default="building"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )
    op.create_index("ix_indexes_workspace_id", "indexes", ["workspace_id"])
    op.create_index("ix_indexes_status", "indexes", ["status"])

    # experiments
    op.create_table(
        "experiments",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "workspace_id",
            UUID(as_uuid=True),
            sa.ForeignKey("workspaces.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "index_id",
            UUID(as_uuid=True),
            sa.ForeignKey("indexes.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("config", JSONB, nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )
    op.create_index("ix_experiments_workspace_id", "experiments", ["workspace_id"])
    op.create_index("ix_experiments_index_id", "experiments", ["index_id"])

    # runs
    op.create_table(
        "runs",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "experiment_id",
            UUID(as_uuid=True),
            sa.ForeignKey("experiments.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("status", sa.String(32), nullable=False, server_default="queued"),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("artifact_uri", sa.Text, nullable=True),
        sa.Column("logs", JSONB, nullable=True),
    )
    op.create_index("ix_runs_experiment_id", "runs", ["experiment_id"])
    op.create_index("ix_runs_status", "runs", ["status"])

    # eval_cases
    op.create_table(
        "eval_cases",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "run_id",
            UUID(as_uuid=True),
            sa.ForeignKey("runs.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("question", sa.Text, nullable=True),
        sa.Column("ground_truth", sa.Text, nullable=True),
        sa.Column("predicted", sa.Text, nullable=True),
        sa.Column("metrics", JSONB, nullable=True),
        sa.Column("failure_type", sa.String(64), nullable=True),
    )
    op.create_index("ix_eval_cases_run_id", "eval_cases", ["run_id"])

    # metric_snapshots
    op.create_table(
        "metric_snapshots",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "run_id",
            UUID(as_uuid=True),
            sa.ForeignKey("runs.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("metrics", JSONB, nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )
    op.create_index("ix_metric_snapshots_run_id", "metric_snapshots", ["run_id"])

    # deployments
    op.create_table(
        "deployments",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "workspace_id",
            UUID(as_uuid=True),
            sa.ForeignKey("workspaces.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "index_id",
            UUID(as_uuid=True),
            sa.ForeignKey("indexes.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("environment", sa.String(32), nullable=True),
        sa.Column("revision", sa.String(64), nullable=True),
        sa.Column("status", sa.String(32), nullable=False, server_default="pending"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )
    op.create_index("ix_deployments_workspace_id", "deployments", ["workspace_id"])
    op.create_index("ix_deployments_status", "deployments", ["status"])


def downgrade() -> None:
    op.drop_table("deployments")
    op.drop_table("metric_snapshots")
    op.drop_table("eval_cases")
    op.drop_table("runs")
    op.drop_table("experiments")
    op.drop_table("indexes")
