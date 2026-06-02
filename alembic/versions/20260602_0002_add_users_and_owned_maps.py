"""add users and owned maps

Revision ID: 20260602_0002
Revises: 20260602_0001
Create Date: 2026-06-02
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "20260602_0002"
down_revision: str | None = "20260602_0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)
    op.create_index(op.f("ix_users_id"), "users", ["id"], unique=False)

    op.create_table(
        "maps",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("owner_id", sa.Integer(), nullable=False),
        sa.Column("map_id", sa.String(length=64), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("description", sa.String(length=500), nullable=False),
        sa.Column("width", sa.Float(), nullable=False),
        sa.Column("height", sa.Float(), nullable=False),
        sa.Column("coordinate_unit", sa.String(length=24), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["owner_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("owner_id", "map_id", name="uq_maps_owner_map_id"),
    )
    op.create_index(op.f("ix_maps_id"), "maps", ["id"], unique=False)
    op.create_index(op.f("ix_maps_map_id"), "maps", ["map_id"], unique=False)
    op.create_index(op.f("ix_maps_owner_id"), "maps", ["owner_id"], unique=False)

    op.add_column("routes", sa.Column("owner_id", sa.Integer(), nullable=True))
    op.create_index(op.f("ix_routes_owner_id"), "routes", ["owner_id"], unique=False)
    op.create_foreign_key("fk_routes_owner_id_users", "routes", "users", ["owner_id"], ["id"], ondelete="CASCADE")

    users_table = sa.table(
        "users",
        sa.column("id", sa.Integer),
        sa.column("email", sa.String),
        sa.column("password_hash", sa.String),
    )
    maps_table = sa.table(
        "maps",
        sa.column("owner_id", sa.Integer),
        sa.column("map_id", sa.String),
        sa.column("name", sa.String),
        sa.column("description", sa.String),
        sa.column("width", sa.Float),
        sa.column("height", sa.Float),
        sa.column("coordinate_unit", sa.String),
    )
    routes_table = sa.table("routes", sa.column("owner_id", sa.Integer))

    op.bulk_insert(
        users_table,
        [
            {
                "id": 1,
                "email": "legacy@example.local",
                "password_hash": "legacy-disabled-password-hash",
            }
        ],
    )
    op.execute("SELECT setval(pg_get_serial_sequence('users', 'id'), COALESCE((SELECT MAX(id) FROM users), 1), true)")
    op.bulk_insert(
        maps_table,
        [
            {
                "owner_id": 1,
                "map_id": "small_loop",
                "name": "Small loop",
                "description": "Compact loop for basic autonomous driving tests.",
                "width": 300,
                "height": 200,
                "coordinate_unit": "cm",
            },
            {
                "owner_id": 1,
                "map_id": "crossroads",
                "name": "Crossroads",
                "description": "Intersection layout for route and turning scenarios.",
                "width": 400,
                "height": 400,
                "coordinate_unit": "cm",
            },
            {
                "owner_id": 1,
                "map_id": "parking",
                "name": "Parking",
                "description": "Parking area layout for precise maneuvers.",
                "width": 500,
                "height": 300,
                "coordinate_unit": "cm",
            },
        ],
    )
    op.execute(routes_table.update().values(owner_id=1))
    op.alter_column("routes", "owner_id", existing_type=sa.Integer(), nullable=False)


def downgrade() -> None:
    op.drop_constraint("fk_routes_owner_id_users", "routes", type_="foreignkey")
    op.drop_index(op.f("ix_routes_owner_id"), table_name="routes")
    op.drop_column("routes", "owner_id")
    op.drop_index(op.f("ix_maps_owner_id"), table_name="maps")
    op.drop_index(op.f("ix_maps_map_id"), table_name="maps")
    op.drop_index(op.f("ix_maps_id"), table_name="maps")
    op.drop_table("maps")
    op.drop_index(op.f("ix_users_id"), table_name="users")
    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_table("users")
