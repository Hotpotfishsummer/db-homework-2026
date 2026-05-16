from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import String, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from db.base import Base


def _utcnow():
    return datetime.now(timezone.utc)


class OutfitRecommendation(Base):
    __tablename__ = "outfit_recommendations"

    recommend_id:    Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id:         Mapped[int] = mapped_column(ForeignKey("users.user_id", ondelete="CASCADE"))
    weather_context: Mapped[Optional[dict]] = mapped_column(JSONB)
    analysis_doc:    Mapped[str] = mapped_column(Text, nullable=False)
    selected_items:  Mapped[Optional[list]] = mapped_column(JSONB)
    created_at:      Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)

    user: Mapped["User"] = relationship(back_populates="recommendations")
