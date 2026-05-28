"""init schema

Revision ID: c0fd52f978c6
Revises: 
Create Date: 2026-05-16 17:06:02.944861

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from db.base import Base
from db.models import User, WardrobeItem, OutfitRecommendation, TryonResult


# revision identifiers, used by Alembic.
revision: str = 'c0fd52f978c6'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create base tables from SQLAlchemy metadata for initial schema setup.
    bind = op.get_bind()
    Base.metadata.create_all(bind=bind, checkfirst=True)


def downgrade() -> None:
    """Downgrade schema."""
    bind = op.get_bind()
    Base.metadata.drop_all(bind=bind, checkfirst=True)
