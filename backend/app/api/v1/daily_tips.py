from fastapi import APIRouter, Depends
from app.core.security import get_current_user
from app.services.ai import AIService

router = APIRouter(prefix="/daily-tips", tags=["daily_tips"])
ai = AIService()


@router.get("/")
async def get_daily_tip(user: dict = Depends(get_current_user)):
    """Fetch AI-generated daily outfit tip based on weather + wardrobe."""
    tip = await ai.get_daily_tips(user_id=user.get("user_id"))
    return {"tip": tip, "user_id": user.get("user_id")}
