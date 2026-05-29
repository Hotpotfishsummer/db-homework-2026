from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import String, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from db.base import Base


def _utcnow():
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    user_id:       Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username:      Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    display_name:    Mapped[Optional[str]] = mapped_column(String(100))
    style_preference: Mapped[Optional[str]] = mapped_column(String(200))
    location:         Mapped[Optional[str]] = mapped_column(String(100))
    created_at:       Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)

    clothes: Mapped[list["Clothes"]] = relationship(back_populates="user", cascade="all, delete-orphan")
