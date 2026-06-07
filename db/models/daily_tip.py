from __future__ import annotations

from datetime import date, datetime, timezone

from sqlalchemy import CheckConstraint, Date, DateTime, ForeignKey, Index, String, Text, UniqueConstraint, desc
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.base import Base


def _utcnow():
    return datetime.now(timezone.utc)


class DailyTip(Base):
    __tablename__ = "daily_tips"
    __table_args__ = (
        CheckConstraint("tip_type IN ('outfit', 'care')", name="ck_daily_tips_type"),
        UniqueConstraint("user_id", "tip_date", name="uq_daily_tips_user_date"),
        Index("ix_daily_tips_user_date", "user_id", desc("tip_date")),
    )

    tip_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    tip_date: Mapped[date] = mapped_column(Date, nullable=False)
    tip_type: Mapped[str] = mapped_column(String(20), default="outfit", nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow, nullable=False)

    user: Mapped["User"] = relationship(back_populates="daily_tips")
