from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    SmallInteger,
    String,
    Text,
    Uuid,
    desc,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.base import Base


def _utcnow():
    return datetime.now(timezone.utc)


class OutfitRecommendation(Base):
    __tablename__ = "outfit_recommendations"
    __table_args__ = (
        CheckConstraint(
            "scene IN ('commute', 'date', 'casual', 'sports', 'party')",
            name="ck_outfit_recommendations_scene",
        ),
        CheckConstraint(
            "match_rate BETWEEN 0 AND 100",
            name="ck_outfit_recommendations_match_rate",
        ),
        Index("ix_outfit_recommendations_user_created", "user_id", desc("created_at")),
    )

    recommend_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    scene: Mapped[str] = mapped_column(String(20), nullable=False)
    weather_snapshot: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    title: Mapped[str] = mapped_column(String(150), nullable=False)
    content: Mapped[str] = mapped_column(Text, default="", nullable=False)
    match_rate: Mapped[int] = mapped_column(SmallInteger, default=0, nullable=False)
    image_url: Mapped[Optional[str]] = mapped_column(String(500))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow, nullable=False)

    user: Mapped["User"] = relationship(back_populates="outfit_recommendations")
    items: Mapped[list["RecommendationItem"]] = relationship(
        back_populates="recommendation", cascade="all, delete-orphan", passive_deletes=True, lazy="selectin"
    )
    favorites: Mapped[list["OutfitFavorite"]] = relationship(
        back_populates="recommendation", cascade="all, delete-orphan", passive_deletes=True
    )
    history_entries: Mapped[list["OutfitHistory"]] = relationship(
        back_populates="recommendation", cascade="all, delete-orphan", passive_deletes=True
    )


class RecommendationItem(Base):
    __tablename__ = "recommendation_items"
    __table_args__ = (Index("ix_recommendation_items_item_id", "item_id"),)

    recommend_id: Mapped[UUID] = mapped_column(
        ForeignKey("outfit_recommendations.recommend_id", ondelete="CASCADE"), primary_key=True
    )
    item_id: Mapped[int] = mapped_column(ForeignKey("clothes.item_id"), primary_key=True)
    slot: Mapped[Optional[str]] = mapped_column(String(20))
    sort_order: Mapped[int] = mapped_column(default=0, nullable=False)
    item_snapshot: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)

    recommendation: Mapped["OutfitRecommendation"] = relationship(back_populates="items")
    item: Mapped["Clothes"] = relationship(back_populates="recommendation_items")
