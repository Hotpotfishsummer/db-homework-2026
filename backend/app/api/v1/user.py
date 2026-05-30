from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.schemas import UserProfile, UserProfileUpdate
from app.core.security import require_user
from db import get_db, UserRepository, ClothesRepository

router = APIRouter(prefix="/user", tags=["user"])


def _serialize_user_profile(user, wardrobe_count: int) -> UserProfile:
    return UserProfile(
        user_id=user.user_id,
        username=user.username,
        display_name=user.display_name,
        style_preference=user.style_preference,
        location=user.location,
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
    updated = await user_repository.update(
        user["user_id"],
        display_name=payload.display_name,
        style_preference=payload.style_preference,
        location=payload.location,
    )
    if updated is None:
        return _serialize_user_profile(user, 0)

    wardrobe_count = await wardrobe_repository.count_by_user(updated.user_id)
    return _serialize_user_profile(updated, wardrobe_count)
