from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from db.base import Base


def _utcnow():
    return datetime.now(timezone.utc)


class WardrobeItem(Base):
    __tablename__ = "wardrobe_items"

    item_id:    Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id:    Mapped[int] = mapped_column(ForeignKey("users.user_id", ondelete="CASCADE"))
    image_url:  Mapped[str] = mapped_column(String(255), nullable=False)
    category:   Mapped[Optional[str]] = mapped_column(String(50))
    attributes: Mapped[Optional[dict]] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)

    user: Mapped["User"] = relationship(back_populates="wardrobe_items")
