"""add shopping_recommendations

Revision ID: 0002_shopping
Revises: 0001_ai_wardrobe
Create Date: 2026-06-16
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "0002_shopping"
down_revision: Union[str, Sequence[str], None] = "0001_ai_wardrobe"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "shopping_recommendations",
        sa.Column("recommend_id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("category", sa.String(length=32), nullable=False),
        sa.Column("name", sa.String(length=150), nullable=False),
        sa.Column("color", sa.String(length=50), nullable=True),
        sa.Column(
            "style_tags",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'[]'::jsonb"),
            nullable=False,
        ),
        sa.Column("price_range", sa.String(length=50), nullable=True),
        sa.Column("purchase_url", sa.String(length=500), nullable=True),
        sa.Column("reason", sa.Text(), server_default="", nullable=False),
        sa.Column("priority", sa.SmallInteger(), server_default="50", nullable=False),
        sa.Column("status", sa.String(length=20), server_default="pending", nullable=False),
        sa.Column("scene", sa.String(length=20), nullable=True),
        sa.Column(
            "weather_snapshot",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'{}'::jsonb"),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "category IN ('top', 'bottom', 'outerwear', 'shoes', 'accessory', 'bag', 'other')",
            name="ck_shopping_recommendations_category",
        ),
        sa.CheckConstraint(
            "status IN ('pending', 'bought', 'dismissed', 'wishlist')",
            name="ck_shopping_recommendations_status",
        ),
        sa.CheckConstraint(
            "priority BETWEEN 0 AND 100",
            name="ck_shopping_recommendations_priority",
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.user_id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("recommend_id"),
    )
    op.create_index(
        "ix_shopping_recommendations_user_created",
        "shopping_recommendations",
        ["user_id", sa.text("created_at DESC")],
    )
    op.create_index(
        "ix_shopping_recommendations_user_status",
        "shopping_recommendations",
        ["user_id", "status"],
    )


def downgrade() -> None:
    op.drop_index("ix_shopping_recommendations_user_status", table_name="shopping_recommendations")
    op.drop_index("ix_shopping_recommendations_user_created", table_name="shopping_recommendations")
    op.drop_table("shopping_recommendations")
