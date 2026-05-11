from fastapi import APIRouter, Depends
from app.core.security import require_user

router = APIRouter(prefix="/user", tags=["user"])


@router.get("/me")
async def get_profile(user: dict = Depends(require_user)):
    """Get current user profile — DB integration pending."""
    return {
        "user_id": user["user_id"],
        "role": user.get("role", "member"),
        "wardrobe_count": 0,
    }


@router.patch("/me")
async def update_profile(user: dict = Depends(require_user)):
    """Update user profile — DB integration pending."""
    return {"status": "ok", "user_id": user["user_id"]}
