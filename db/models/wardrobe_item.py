from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, String, desc
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.base import Base


def _utcnow():
    return datetime.now(timezone.utc)


class Clothes(Base):
    __tablename__ = "clothes"
    __table_args__ = (
        CheckConstraint(
            "category IN ('top', 'bottom', 'outerwear', 'shoes', 'accessory', 'bag', 'other')",
            name="ck_clothes_category",
        ),
        CheckConstraint("status IN ('available', 'washing')", name="ck_clothes_status"),
        Index("ix_clothes_user_deleted_created", "user_id", "deleted_at", desc("created_at")),
        Index("ix_clothes_user_category_status", "user_id", "category", "status"),
        Index("ix_clothes_seasons_gin", "seasons", postgresql_using="gin"),
    )

    item_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    image_url: Mapped[str] = mapped_column(String(500), nullable=False)
    category: Mapped[str] = mapped_column(String(32), nullable=False, default="other")
    color: Mapped[Optional[str]] = mapped_column(String(50))
    seasons: Mapped[list] = mapped_column(JSONB, default=list, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="available", nullable=False)
    attributes: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow, nullable=False)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    user: Mapped["User"] = relationship(back_populates="clothes")
    recommendation_items: Mapped[list["RecommendationItem"]] = relationship(back_populates="item")


WardrobeItem = Clothes
