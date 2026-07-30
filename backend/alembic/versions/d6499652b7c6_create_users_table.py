"""create users table

Revision ID: d6499652b7c6
Revises: 
Create Date: 2026-07-30 07:17:19.466926

"""
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = 'd6499652b7c6'
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("password_hash", sa.String(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )



def downgrade() -> None:
    op.drop_table("users")
