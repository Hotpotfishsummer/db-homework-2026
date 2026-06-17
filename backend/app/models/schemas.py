from pydantic import BaseModel
from pydantic import Field
from datetime import datetime
from typing import Literal


# ---------------- User-supplied LLM test schemas (new) ----------------

class TestKeyRequest(BaseModel):
    """Schema for POST /api/v1/user/llm/test-key."""
    api_key: str = Field(..., min_length=1, max_length=500)
    base_url: str = Field(..., min_length=1, max_length=500)


class TestKeyResponse(BaseModel):
    """Response for /user/llm/test-key."""
    available: bool
    model_count: int = 0
    models_sample: list[str] = Field(default_factory=list)
    message: str = ""


class TestVisionResponse(BaseModel):
    """Response for /user/llm/test-vision (multipart upload)."""
    multimodal_ok: bool
    response_text: str = ""
    error: str | None = None


class ListModelsResponse(BaseModel):
    """Response for GET /user/llm/models."""
    available: bool
    models: list[str] = Field(default_factory=list)
    message: str = ""


# ---------------- AI Recommendation schemas (new) ----------------

class ItemRecommendRequest(BaseModel):
    """Schema for /api/v1/recommend/items — recommend new shopping items."""
    scene: Literal["commute", "date", "casual", "sports", "party"]
    gapFocus: Literal["top", "bottom", "outerwear", "shoes", "accessory", "bag", "other"] | None = None


class ShoppingItem(BaseModel):
    """Single recommended shopping item."""
    id: str | None = None
    name: str
    category: str
    color: str | None = None
    style_tags: list[str] = Field(default_factory=list)
    price_range: str | None = None
    purchase_url: str | None = None
    reason: str = ""
    priority: int = 50
    status: str = "pending"


class ItemRecommendResponse(BaseModel):
    """Schema for items recommendation response."""
    items: list[ShoppingItem]
    scene: str
    weatherSummary: str | None = None
    toolSummary: list[str] = Field(default_factory=list)
    generatedBy: str = "fallback"


class ItemRecommendEnvelope(BaseModel):
    """Envelope for /api/v1/recommend/items."""
    code: int = 200
    data: ItemRecommendResponse
    msg: str = "success"


class ItemStatusUpdate(BaseModel):
    """Schema for PATCH /api/v1/recommend/items/{id}."""
    status: Literal["pending", "bought", "dismissed", "wishlist"]


class ShoppingOutfitRequest(BaseModel):
    """Schema for /api/v1/recommend/items/with-outfit — embed new items into an outfit."""
    scene: Literal["commute", "date", "casual", "sports", "party"]


class ShoppingOutfitSlot(BaseModel):
    """Single slot in a shopping-outfit (could be owned or need_buy)."""
    category: str
    name: str
    need_buy: bool
    wardrobe_id: int | None = None
    image: str | None = None
    reason: str = ""


class ShoppingOutfitData(BaseModel):
    """Outfit composed of owned + need_buy items."""
    id: str
    name: str
    description: str = ""
    matchRate: int = 0
    scene: str
    slots: list[ShoppingOutfitSlot]


class ShoppingOutfitResponse(BaseModel):
    """Schema for shopping-outfit response."""
    outfit: ShoppingOutfitData
    weatherSummary: str | None = None
    toolSummary: list[str] = Field(default_factory=list)
    generatedBy: str = "fallback"


class ShoppingOutfitEnvelope(BaseModel):
    """Envelope for /api/v1/recommend/items/with-outfit."""
    code: int = 200
    data: ShoppingOutfitResponse
    msg: str = "success"


class WardrobeGapItem(BaseModel):
    """Single category-level gap entry."""
    category: str
    current: int
    suggested: int
    advice: str


class WardrobeGapReport(BaseModel):
    """Schema for /api/v1/recommend/gap-analysis."""
    summary: str
    gaps: list[WardrobeGapItem]
    total_items: int = 0
    dominant_colors: list[dict] = Field(default_factory=list)
    generatedBy: str = "fallback"


class WardrobeGapEnvelope(BaseModel):
    """Envelope for /api/v1/recommend/gap-analysis."""
    code: int = 200
    data: dict
    msg: str = "success"


# ---------------- Existing schemas below ----------------


class GarmentUpload(BaseModel):
    """Schema for garment upload metadata."""
    category: Literal["top", "bottom", "outerwear", "shoes", "accessory"]
    color: str | None = None
    season: Literal["spring", "summer", "autumn", "winter", "all"] = "all"
    tags: list[str] = Field(default_factory=list)


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
    user_id: int
    username: str
    display_name: str | None = None
    style_preference: str | None = None
    location: str | None = None
    wardrobe_count: int = 0
    created_at: datetime | None = None


class UserProfileUpdate(BaseModel):
    """Schema for updating user profile."""
    display_name: str | None = None
    style_preference: str | None = None
    location: str | None = None


class AuthRegisterRequest(BaseModel):
    """Schema for user registration."""
    username: str
    password: str
    display_name: str | None = None
    style_preference: str | None = None
    location: str | None = None


class AuthLoginRequest(BaseModel):
    """Schema for user login."""
    username: str
    password: str


class AuthUserResponse(BaseModel):
    """Schema for authenticated user response."""
    user_id: int
    username: str
    display_name: str | None = None
    style_preference: str | None = None
    location: str | None = None
    wardrobe_count: int = 0
    created_at: datetime | None = None


class AuthResponse(BaseModel):
    """Schema for auth response."""
    access_token: str
    token_type: str = "bearer"
    user: AuthUserResponse


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


class GarmentDetectionResponse(BaseModel):
    """Schema for garment detection response."""
    contains_garment: bool
    confidence: float = Field(..., ge=0.0, le=1.0)
    description: str


class GarmentUploadResponse(BaseModel):
    """Schema for uploaded garment with detection and tagging results."""
    contains_garment: bool
    detection: GarmentDetectionResponse
    analysis: dict
    garment: dict | None = None
