from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_user
from app.services.styling_agent import StylingAgentService
from db import get_db

router = APIRouter(prefix="/daily-tips", tags=["daily_tips"])


@router.get("/")
async def get_daily_tip(
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Fetch AI-generated daily outfit tip based on weather + wardrobe.

    The LangChain Agent queries current weather and wardrobe to provide
    a personalized daily styling suggestion.
    """
    agent = StylingAgentService(db)
    tip = await agent.generate_daily_tip(
        user_id=user.get("user_id"),
        location=user.get("location"),
    )
    return {"tip": tip, "user_id": user.get("user_id")}
