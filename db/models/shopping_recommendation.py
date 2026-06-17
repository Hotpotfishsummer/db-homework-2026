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
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from db.base import Base


def _utcnow():
    return datetime.now(timezone.utc)


class ShoppingRecommendation(Base):
    """AI-recommended shopping items (items the user might want to buy).

    Distinct from `outfit_recommendations` which represents a *complete outfit*
    made of items already in the wardrobe. A ShoppingRecommendation is a single
    new item the AI suggests the user purchase, optionally attached to an
    outfit slot for "buy + match" scenarios.
    """

    __tablename__ = "shopping_recommendations"
    __table_args__ = (
        CheckConstraint(
            "category IN ('top', 'bottom', 'outerwear', 'shoes', 'accessory', 'bag', 'other')",
            name="ck_shopping_recommendations_category",
        ),
        CheckConstraint(
            "status IN ('pending', 'bought', 'dismissed', 'wishlist')",
            name="ck_shopping_recommendations_status",
        ),
        CheckConstraint(
            "priority BETWEEN 0 AND 100",
            name="ck_shopping_recommendations_priority",
        ),
        Index("ix_shopping_recommendations_user_created", "user_id", desc("created_at")),
        Index("ix_shopping_recommendations_user_status", "user_id", "status"),
    )

    recommend_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    category: Mapped[str] = mapped_column(String(32), nullable=False, default="other")
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    color: Mapped[Optional[str]] = mapped_column(String(50))
    style_tags: Mapped[list] = mapped_column(JSONB, default=list, nullable=False)
    price_range: Mapped[Optional[str]] = mapped_column(String(50))
    purchase_url: Mapped[Optional[str]] = mapped_column(String(500))
    reason: Mapped[str] = mapped_column(Text, default="", nullable=False)
    priority: Mapped[int] = mapped_column(SmallInteger, default=50, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="pending", nullable=False)
    scene: Mapped[Optional[str]] = mapped_column(String(20))
    weather_snapshot: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow, nullable=False)
