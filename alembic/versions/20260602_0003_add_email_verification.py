"""add email verification fields

Revision ID: 20260602_0003
Revises: 20260602_0002
Create Date: 2026-06-02
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "20260602_0003"
down_revision: str | None = "20260602_0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("users", sa.Column("email_verified", sa.Boolean(), nullable=False, server_default=sa.true()))
    op.add_column("users", sa.Column("email_verification_token_hash", sa.String(length=64), nullable=True))
    op.add_column("users", sa.Column("email_verification_expires_at", sa.DateTime(timezone=True), nullable=True))
    op.create_index(op.f("ix_users_email_verified"), "users", ["email_verified"], unique=False)
    op.create_index(
        op.f("ix_users_email_verification_token_hash"),
        "users",
        ["email_verification_token_hash"],
        unique=False,
    )
    op.alter_column("users", "email_verified", server_default=None)


def downgrade() -> None:
    op.drop_index(op.f("ix_users_email_verification_token_hash"), table_name="users")
    op.drop_index(op.f("ix_users_email_verified"), table_name="users")
    op.drop_column("users", "email_verification_expires_at")
    op.drop_column("users", "email_verification_token_hash")
    op.drop_column("users", "email_verified")
