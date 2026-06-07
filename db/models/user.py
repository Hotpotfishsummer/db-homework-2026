from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.base import Base


def _utcnow():
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, onupdate=_utcnow, nullable=False
    )

    profile: Mapped[Optional["UserProfile"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
        single_parent=True,
        lazy="selectin",
        uselist=False,
    )
    clothes: Mapped[list["Clothes"]] = relationship(
        back_populates="user", cascade="all, delete-orphan", passive_deletes=True
    )
    outfit_recommendations: Mapped[list["OutfitRecommendation"]] = relationship(
        back_populates="user", cascade="all, delete-orphan", passive_deletes=True
    )
    favorites: Mapped[list["OutfitFavorite"]] = relationship(
        back_populates="user", cascade="all, delete-orphan", passive_deletes=True
    )
    outfit_history: Mapped[list["OutfitHistory"]] = relationship(
        back_populates="user", cascade="all, delete-orphan", passive_deletes=True
    )
    daily_tips: Mapped[list["DailyTip"]] = relationship(
        back_populates="user", cascade="all, delete-orphan", passive_deletes=True
    )

    def _ensure_profile(self) -> "UserProfile":
        if self.profile is None:
            from db.models.user_profile import UserProfile

            self.profile = UserProfile()
        return self.profile

    # Compatibility properties for backend code that previously read profile
    # fields directly from users.
    @property
    def display_name(self) -> Optional[str]:
        return self.profile.display_name if self.profile else None

    @display_name.setter
    def display_name(self, value: Optional[str]) -> None:
        self._ensure_profile().display_name = value

    @property
    def style_preference(self) -> Optional[str]:
        return self.profile.style_preference if self.profile else None

    @style_preference.setter
    def style_preference(self, value: Optional[str]) -> None:
        self._ensure_profile().style_preference = value

    @property
    def location(self) -> Optional[str]:
        return self.profile.location if self.profile else None

    @location.setter
    def location(self, value: Optional[str]) -> None:
        self._ensure_profile().location = value
