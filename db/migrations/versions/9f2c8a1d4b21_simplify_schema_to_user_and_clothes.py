"""simplify schema to user and clothes

Revision ID: 9f2c8a1d4b21
Revises: c0fd52f978c6
Create Date: 2026-05-29 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "9f2c8a1d4b21"
down_revision: Union[str, Sequence[str], None] = "c0fd52f978c6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if inspector.has_table("wardrobe_items") and not inspector.has_table("clothes"):
        op.rename_table("wardrobe_items", "clothes")

    if inspector.has_table("outfit_recommendations"):
        op.drop_table("outfit_recommendations")

    if inspector.has_table("tryon_results"):
        op.drop_table("tryon_results")


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if inspector.has_table("clothes") and not inspector.has_table("wardrobe_items"):
        op.rename_table("clothes", "wardrobe_items")

    if not inspector.has_table("outfit_recommendations"):
        op.create_table(
            "outfit_recommendations",
            sa.Column("recommend_id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False),
            sa.Column("weather_context", sa.JSON(), nullable=True),
            sa.Column("analysis_doc", sa.Text(), nullable=False),
            sa.Column("selected_items", sa.JSON(), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        )

    if not inspector.has_table("tryon_results"):
        op.create_table(
            "tryon_results",
            sa.Column("tryon_id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False),
            sa.Column("base_image_url", sa.String(length=255), nullable=False),
            sa.Column("result_image_url", sa.String(length=255), nullable=False),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        )