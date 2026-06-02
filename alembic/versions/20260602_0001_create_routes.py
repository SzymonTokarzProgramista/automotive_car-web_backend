"""create routes table

Revision ID: 20260602_0001
Revises:
Create Date: 2026-06-02
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "20260602_0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "routes",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("map_id", sa.String(length=64), nullable=False),
        sa.Column("start_x", sa.Float(), nullable=False),
        sa.Column("start_y", sa.Float(), nullable=False),
        sa.Column("start_heading", sa.Float(), nullable=True),
        sa.Column("end_x", sa.Float(), nullable=False),
        sa.Column("end_y", sa.Float(), nullable=False),
        sa.Column("end_heading", sa.Float(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("is_current", sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_routes_id"), "routes", ["id"], unique=False)
    op.create_index(op.f("ix_routes_is_current"), "routes", ["is_current"], unique=False)
    op.create_index(op.f("ix_routes_map_id"), "routes", ["map_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_routes_map_id"), table_name="routes")
    op.drop_index(op.f("ix_routes_is_current"), table_name="routes")
    op.drop_index(op.f("ix_routes_id"), table_name="routes")
    op.drop_table("routes")

