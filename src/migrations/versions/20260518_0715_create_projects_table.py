"""create projects table

Revision ID: 20260518_0715
Revises: 20260518_0714
Create Date: 2026-05-18 07:15:00.000000
"""

from collections.abc import Sequence
from typing import Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "20260518_0715"
down_revision: Union[str, Sequence[str], None] = "20260518_0714"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "project",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("owner_user_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("description", sa.String(length=63206), nullable=True),
        sa.Column("uuid", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_deleted", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(["owner_user_id"], ["user.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("uuid"),
    )
    op.create_index(op.f("ix_project_is_deleted"), "project", ["is_deleted"], unique=False)
    op.create_index(op.f("ix_project_owner_user_id"), "project", ["owner_user_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_project_owner_user_id"), table_name="project")
    op.drop_index(op.f("ix_project_is_deleted"), table_name="project")
    op.drop_table("project")
