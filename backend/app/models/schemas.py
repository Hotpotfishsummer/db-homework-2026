from pydantic import BaseModel
from pydantic import Field
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


class DailyStylingAdvice(BaseModel):
    """Schema for daily styling advice returned by the agent."""
    user_id: str | None = None
    tip: str
    weather_summary: str | None = None
    wardrobe_items_considered: int = 0
    generated_by: str = "fallback"
    tool_summary: list[str] = Field(default_factory=list)
    raw_output: str | None = None


class StylingRecommendation(BaseModel):
    """Schema for outfit recommendation returned by the agent."""
    id: str
    name: str
    description: str
    matchRate: int
    reason: str
    image: str = ""
    selectedItems: list[int] = Field(default_factory=list)
    weatherSummary: str | None = None
    toolSummary: list[str] = Field(default_factory=list)
    generatedBy: str = "fallback"
    scene: str | None = None
    raw_output: str | None = None


class DailyTipEnvelope(BaseModel):
    """Envelope for the daily tip API."""
    code: int = 200
    data: DailyStylingAdvice
    msg: str = "success"


class StylingRecommendationEnvelope(BaseModel):
    """Envelope for the outfit recommendation API."""
    code: int = 200
    data: StylingRecommendation
    msg: str = "success"
