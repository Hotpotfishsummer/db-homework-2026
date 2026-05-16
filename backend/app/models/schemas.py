from pydantic import BaseModel
from datetime import datetime
from typing import Literal


class GarmentUpload(BaseModel):
    """Schema for garment upload metadata."""
    category: Literal["top", "bottom", "outerwear", "shoes", "accessory"]
    color: str | None = None
    season: Literal["spring", "summer", "autumn", "winter", "all"] = "all"
    tags: list[str] = []


class GarmentResponse(BaseModel):
    """Schema for garment response."""
    id: str
    user_id: str
    image_url: str
    category: str
    color: str | None
    season: str
    tags: list[str]
    created_at: datetime


class DailyTipResponse(BaseModel):
    """Schema for daily tip response."""
    tip: str
    weather_summary: str | None
    generated_at: datetime


class UserProfile(BaseModel):
    """Schema for user profile."""
    user_id: str
    display_name: str | None = None
    style_preference: str | None = None
    location: str | None = None


class OutfitRecommendRequest(BaseModel):
    """Schema for outfit recommendation request."""
    scene: Literal["commute", "date", "casual", "sports", "party"]
    wardrobeIds: list[int]
