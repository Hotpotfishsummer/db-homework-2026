from datetime import datetime, timezone
from sqlalchemy import String, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from db.base import Base


def _utcnow():
    return datetime.now(timezone.utc)


class TryonResult(Base):
    __tablename__ = "tryon_results"

    tryon_id:         Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id:          Mapped[int] = mapped_column(ForeignKey("users.user_id", ondelete="CASCADE"))
    base_image_url:   Mapped[str] = mapped_column(String(255), nullable=False)
    result_image_url: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at:       Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)

    user: Mapped["User"] = relationship(back_populates="tryon_results")
