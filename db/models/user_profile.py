from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.base import Base


def _utcnow():
    return datetime.now(timezone.utc)


class UserProfile(Base):
    __tablename__ = "user_profiles"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.user_id", ondelete="CASCADE"), primary_key=True
    )
    display_name: Mapped[Optional[str]] = mapped_column(String(100))
    avatar_url: Mapped[Optional[str]] = mapped_column(String(500))
    bio: Mapped[Optional[str]] = mapped_column(String(255))
    location: Mapped[Optional[str]] = mapped_column(String(100))
    skin_tone: Mapped[Optional[str]] = mapped_column(String(50))
    body_shape: Mapped[Optional[str]] = mapped_column(String(50))
    preferences: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, onupdate=_utcnow, nullable=False
    )

    user: Mapped["User"] = relationship(back_populates="profile")

    def _get_preference(self, key: str, default=None):
        if not self.preferences:
            return default
        return self.preferences.get(key, default)

    def _set_preference(self, key: str, value) -> None:
        payload = dict(self.preferences or {})
        if value is None or value == {} or value == []:
            payload.pop(key, None)
        else:
            payload[key] = value
        self.preferences = payload

    @property
    def style_preference(self) -> Optional[str]:
        return self._get_preference("style_preference")

    @style_preference.setter
    def style_preference(self, value: Optional[str]) -> None:
        self._set_preference("style_preference", value)

    @property
    def style_axes(self) -> dict:
        return self._get_preference("style_axes", {})

    @style_axes.setter
    def style_axes(self, value: dict | None) -> None:
        self._set_preference("style_axes", value or {})

    @property
    def style_tags(self) -> list:
        return self._get_preference("style_tags", [])

    @style_tags.setter
    def style_tags(self, value: list | None) -> None:
        self._set_preference("style_tags", value or [])

    @property
    def favorite_colors(self) -> list:
        return self._get_preference("favorite_colors", [])

    @favorite_colors.setter
    def favorite_colors(self, value: list | None) -> None:
        self._set_preference("favorite_colors", value or [])

    @property
    def avoid_colors(self) -> list:
        return self._get_preference("avoid_colors", [])

    @avoid_colors.setter
    def avoid_colors(self, value: list | None) -> None:
        self._set_preference("avoid_colors", value or [])

    @property
    def fit_preference(self) -> Optional[str]:
        return self._get_preference("fit_preference")

    @fit_preference.setter
    def fit_preference(self, value: Optional[str]) -> None:
        self._set_preference("fit_preference", value)
