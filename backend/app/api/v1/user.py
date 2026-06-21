from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.schemas import UserProfile, UserProfileUpdate
from app.core.security import require_user
from db import get_db, UserRepository, ClothesRepository

router = APIRouter(prefix="/user", tags=["user"])


def _serialize_user_profile(user, wardrobe_count: int) -> UserProfile:
    db_profile = getattr(user, "profile", None)
    preferences = dict(getattr(db_profile, "preferences", {}) or {}) if db_profile else {}
    return UserProfile(
        user_id=user.user_id,
        username=user.username,
        display_name=user.display_name,
        avatar_url=getattr(db_profile, "avatar_url", None),
        bio=getattr(db_profile, "bio", None),
        style_preference=user.style_preference,
        location=user.location,
        skin_tone=getattr(db_profile, "skin_tone", None),
        body_shape=getattr(db_profile, "body_shape", None),
        preferences=preferences,
        height=preferences.get("height"),
        weight=preferences.get("weight"),
        bmi=preferences.get("bmi"),
        face_feature=preferences.get("face_feature"),
        style_axes=preferences.get("style_axes", {}),
        style_tags=preferences.get("style_tags", []),
        favorite_colors=preferences.get("favorite_colors", []),
        avoid_colors=preferences.get("avoid_colors", []),
        fit_preference=preferences.get("fit_preference"),
        wardrobe_count=wardrobe_count,
        created_at=user.created_at,
    )


@router.get("/me", response_model=UserProfile)
async def get_profile(
    user: dict = Depends(require_user),
    db: AsyncSession = Depends(get_db),
):
    """Get current user profile from the database."""
    user_repository = UserRepository(db)
    wardrobe_repository = ClothesRepository(db)
    user_record = await user_repository.get_by_id(user["user_id"])
    if user_record is None:
        return _serialize_user_profile(user, 0)

    wardrobe_count = await wardrobe_repository.count_by_user(user_record.user_id)
    return _serialize_user_profile(user_record, wardrobe_count)


@router.patch("/me", response_model=UserProfile)
async def update_profile(
    payload: UserProfileUpdate,
    user: dict = Depends(require_user),
    db: AsyncSession = Depends(get_db),
):
    """Update current user profile in the database."""
    user_repository = UserRepository(db)
    wardrobe_repository = ClothesRepository(db)
    current = await user_repository.get_by_id(user["user_id"])
    current_preferences = dict(getattr(getattr(current, "profile", None), "preferences", {}) or {}) if current else {}
    incoming_preferences = dict(payload.preferences or {})
    preference_updates = {
        "height": payload.height,
        "weight": payload.weight,
        "bmi": payload.bmi,
        "face_feature": payload.face_feature,
        "style_axes": payload.style_axes,
        "style_tags": payload.style_tags,
        "favorite_colors": payload.favorite_colors,
        "avoid_colors": payload.avoid_colors,
        "fit_preference": payload.fit_preference,
        "style_preference": payload.style_preference,
    }
    for key, value in preference_updates.items():
        if value is not None:
            incoming_preferences[key] = value
    merged_preferences = {**current_preferences, **incoming_preferences}

    updated = await user_repository.update(
        user["user_id"],
        display_name=payload.display_name,
        avatar_url=payload.avatar_url,
        bio=payload.bio,
        style_preference=payload.style_preference,
        location=payload.location,
        skin_tone=payload.skin_tone,
        body_shape=payload.body_shape,
        preferences=merged_preferences,
    )
    if updated is None:
        return _serialize_user_profile(user, 0)

    wardrobe_count = await wardrobe_repository.count_by_user(updated.user_id)
    return _serialize_user_profile(updated, wardrobe_count)
