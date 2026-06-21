from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_user
from app.core.user_llm import apply_user_llm, parse_user_llm_headers
from app.services.styling_agent import StylingAgentService
from db import get_db

router = APIRouter(prefix="/daily-tips", tags=["daily_tips"])


@router.get("/")
async def get_daily_tip(
    http_request: Request,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Fetch AI-generated daily outfit tip based on weather + wardrobe.

    The LangChain Agent queries current weather and wardrobe to provide
    a personalized daily styling suggestion. If the user supplied their
    own LLM (X-User-LLM-* headers), that LLM is used instead of the
    server's .env-configured one.
    """
    user_llm = parse_user_llm_headers(http_request)
    agent = StylingAgentService(db)
    with apply_user_llm(user_llm):
        tip = await agent.generate_daily_tip(
            user_id=user.get("user_id"),
            location=user.get("location"),
            user_llm=user_llm,
        )
    return {"tip": tip, "user_id": user.get("user_id")}
