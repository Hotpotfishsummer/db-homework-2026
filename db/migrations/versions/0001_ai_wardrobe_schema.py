"""AI wardrobe schema baseline

Revision ID: 0001_ai_wardrobe
Revises:
Create Date: 2026-06-02
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "0001_ai_wardrobe"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("user_id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("username", sa.String(length=50), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.PrimaryKeyConstraint("user_id"),
        sa.UniqueConstraint("username"),
    )

    op.create_table(
        "user_profiles",
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("display_name", sa.String(length=100), nullable=True),
        sa.Column("avatar_url", sa.String(length=500), nullable=True),
        sa.Column("bio", sa.String(length=255), nullable=True),
        sa.Column("location", sa.String(length=100), nullable=True),
        sa.Column("skin_tone", sa.String(length=50), nullable=True),
        sa.Column("body_shape", sa.String(length=50), nullable=True),
        sa.Column("preferences", postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'{}'::jsonb"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.user_id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("user_id"),
    )

    op.create_table(
        "clothes",
        sa.Column("item_id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("image_url", sa.String(length=500), nullable=False),
        sa.Column("category", sa.String(length=32), nullable=False),
        sa.Column("color", sa.String(length=50), nullable=True),
        sa.Column("seasons", postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'[]'::jsonb"), nullable=False),
        sa.Column("status", sa.String(length=20), server_default="available", nullable=False),
        sa.Column("attributes", postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'{}'::jsonb"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint(
            "category IN ('top', 'bottom', 'outerwear', 'shoes', 'accessory', 'bag', 'other')",
            name="ck_clothes_category",
        ),
        sa.CheckConstraint("status IN ('available', 'washing')", name="ck_clothes_status"),
        sa.ForeignKeyConstraint(["user_id"], ["users.user_id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("item_id"),
    )
    op.create_index("ix_clothes_user_deleted_created", "clothes", ["user_id", "deleted_at", sa.text("created_at DESC")])
    op.create_index("ix_clothes_user_category_status", "clothes", ["user_id", "category", "status"])
    op.create_index("ix_clothes_seasons_gin", "clothes", ["seasons"], postgresql_using="gin")

    op.create_table(
        "outfit_recommendations",
        sa.Column("recommend_id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("scene", sa.String(length=20), nullable=False),
        sa.Column("weather_snapshot", postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'{}'::jsonb"), nullable=False),
        sa.Column("title", sa.String(length=150), nullable=False),
        sa.Column("content", sa.Text(), server_default="", nullable=False),
        sa.Column("match_rate", sa.SmallInteger(), server_default="0", nullable=False),
        sa.Column("image_url", sa.String(length=500), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.CheckConstraint(
            "scene IN ('commute', 'date', 'casual', 'sports', 'party')",
            name="ck_outfit_recommendations_scene",
        ),
        sa.CheckConstraint(
            "match_rate BETWEEN 0 AND 100",
            name="ck_outfit_recommendations_match_rate",
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.user_id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("recommend_id"),
    )
    op.create_index("ix_outfit_recommendations_user_created", "outfit_recommendations", ["user_id", sa.text("created_at DESC")])

    op.create_table(
        "recommendation_items",
        sa.Column("recommend_id", sa.Uuid(), nullable=False),
        sa.Column("item_id", sa.Integer(), nullable=False),
        sa.Column("slot", sa.String(length=20), nullable=True),
        sa.Column("sort_order", sa.SmallInteger(), server_default="0", nullable=False),
        sa.Column("item_snapshot", postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'{}'::jsonb"), nullable=False),
        sa.ForeignKeyConstraint(["item_id"], ["clothes.item_id"]),
        sa.ForeignKeyConstraint(["recommend_id"], ["outfit_recommendations.recommend_id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("recommend_id", "item_id"),
    )
    op.create_index("ix_recommendation_items_item_id", "recommendation_items", ["item_id"])

    op.create_table(
        "outfit_favorites",
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("recommend_id", sa.Uuid(), nullable=False),
        sa.Column("favorited_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.ForeignKeyConstraint(["recommend_id"], ["outfit_recommendations.recommend_id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.user_id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("user_id", "recommend_id"),
    )
    op.create_index("ix_outfit_favorites_user_favorited", "outfit_favorites", ["user_id", sa.text("favorited_at DESC")])

    op.create_table(
        "outfit_history",
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("recommend_id", sa.Uuid(), nullable=False),
        sa.Column("first_viewed_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("last_viewed_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("view_count", sa.Integer(), server_default="1", nullable=False),
        sa.Column("last_action", sa.String(length=20), nullable=False),
        sa.CheckConstraint("last_action IN ('detail', 'liked', 'skipped')", name="ck_outfit_history_action"),
        sa.ForeignKeyConstraint(["recommend_id"], ["outfit_recommendations.recommend_id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.user_id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("user_id", "recommend_id"),
    )
    op.create_index("ix_outfit_history_user_last_viewed", "outfit_history", ["user_id", sa.text("last_viewed_at DESC")])

    op.create_table(
        "daily_tips",
        sa.Column("tip_id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("tip_date", sa.Date(), nullable=False),
        sa.Column("tip_type", sa.String(length=20), server_default="outfit", nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.CheckConstraint("tip_type IN ('outfit', 'care')", name="ck_daily_tips_type"),
        sa.ForeignKeyConstraint(["user_id"], ["users.user_id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("tip_id"),
        sa.UniqueConstraint("user_id", "tip_date", name="uq_daily_tips_user_date"),
    )
    op.create_index("ix_daily_tips_user_date", "daily_tips", ["user_id", sa.text("tip_date DESC")])


def downgrade() -> None:
    op.drop_index("ix_daily_tips_user_date", table_name="daily_tips")
    op.drop_table("daily_tips")
    op.drop_index("ix_outfit_history_user_last_viewed", table_name="outfit_history")
    op.drop_table("outfit_history")
    op.drop_index("ix_outfit_favorites_user_favorited", table_name="outfit_favorites")
    op.drop_table("outfit_favorites")
    op.drop_index("ix_recommendation_items_item_id", table_name="recommendation_items")
    op.drop_table("recommendation_items")
    op.drop_index("ix_outfit_recommendations_user_created", table_name="outfit_recommendations")
    op.drop_table("outfit_recommendations")
    op.drop_index("ix_clothes_seasons_gin", table_name="clothes", postgresql_using="gin")
    op.drop_index("ix_clothes_user_category_status", table_name="clothes")
    op.drop_index("ix_clothes_user_deleted_created", table_name="clothes")
    op.drop_table("clothes")
    op.drop_table("user_profiles")
    op.drop_table("users")
