"""Add experiments.config_hash for reproducible config identity.

Revision ID: 0005
Revises: 0004
Create Date: 2026-04-18

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0005"
down_revision: Union[str, None] = "0004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "experiments",
        sa.Column("config_hash", sa.String(length=64), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("experiments", "config_hash")
