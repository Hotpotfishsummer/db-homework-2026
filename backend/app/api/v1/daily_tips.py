from fastapi import APIRouter, Depends
from app.core.security import get_current_user
from app.models.schemas import DailyTipEnvelope
from app.services.styling_agent import StylingAgentService

router = APIRouter(prefix="/daily-tips", tags=["daily_tips"])
styling_agent = StylingAgentService()


@router.get("/", response_model=DailyTipEnvelope)
async def get_daily_tip(user: dict = Depends(get_current_user)):
    """Fetch AI-generated daily outfit tip based on weather + wardrobe."""
    tip = await styling_agent.generate_daily_tip(user_id=user.get("user_id"), location=user.get("location"))
    tip["user_id"] = str(user.get("user_id")) if user.get("user_id") is not None else None
    return {"code": 200, "data": tip, "msg": "success"}
