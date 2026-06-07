from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, Integer, String, desc
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.base import Base


def _utcnow():
    return datetime.now(timezone.utc)


class OutfitFavorite(Base):
    __tablename__ = "outfit_favorites"
    __table_args__ = (Index("ix_outfit_favorites_user_favorited", "user_id", desc("favorited_at")),)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id", ondelete="CASCADE"), primary_key=True)
    recommend_id: Mapped[UUID] = mapped_column(
        ForeignKey("outfit_recommendations.recommend_id", ondelete="CASCADE"), primary_key=True
    )
    favorited_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow, nullable=False)

    user: Mapped["User"] = relationship(back_populates="favorites")
    recommendation: Mapped["OutfitRecommendation"] = relationship(back_populates="favorites")


class OutfitHistory(Base):
    __tablename__ = "outfit_history"
    __table_args__ = (
        CheckConstraint("last_action IN ('detail', 'liked', 'skipped')", name="ck_outfit_history_action"),
        Index("ix_outfit_history_user_last_viewed", "user_id", desc("last_viewed_at")),
    )

    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id", ondelete="CASCADE"), primary_key=True)
    recommend_id: Mapped[UUID] = mapped_column(
        ForeignKey("outfit_recommendations.recommend_id", ondelete="CASCADE"), primary_key=True
    )
    first_viewed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow, nullable=False)
    last_viewed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow, nullable=False)
    view_count: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    last_action: Mapped[str] = mapped_column(String(20), nullable=False)

    user: Mapped["User"] = relationship(back_populates="outfit_history")
    recommendation: Mapped["OutfitRecommendation"] = relationship(back_populates="history_entries")
