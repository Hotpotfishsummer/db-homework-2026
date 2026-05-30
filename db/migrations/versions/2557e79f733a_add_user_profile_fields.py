"""add user profile fields

Revision ID: 2557e79f733a
Revises: c0fd52f978c6
Create Date: 2026-05-16 22:13:58.494644

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect
from db.base import Base


# revision identifiers, used by Alembic.
revision: str = '2557e79f733a'
down_revision: Union[str, Sequence[str], None] = 'c0fd52f978c6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    bind = op.get_bind()
    inspector = inspect(bind)

    # Self-heal environments where base tables were not created by a prior migration.
    if not inspector.has_table("users"):
        Base.metadata.create_all(bind=bind, checkfirst=True)
        return

    existing_columns = {column["name"] for column in inspector.get_columns("users")}
    if "display_name" not in existing_columns:
        op.add_column("users", sa.Column("display_name", sa.String(length=100), nullable=True))
    if "style_preference" not in existing_columns:
        op.add_column("users", sa.Column("style_preference", sa.String(length=200), nullable=True))
    if "location" not in existing_columns:
        op.add_column("users", sa.Column("location", sa.String(length=100), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    bind = op.get_bind()
    inspector = inspect(bind)
    if not inspector.has_table("users"):
        return

    existing_columns = {column["name"] for column in inspector.get_columns("users")}
    if "location" in existing_columns:
        op.drop_column("users", "location")
    if "style_preference" in existing_columns:
        op.drop_column("users", "style_preference")
    if "display_name" in existing_columns:
        op.drop_column("users", "display_name")
