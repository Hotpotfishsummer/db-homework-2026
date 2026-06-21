from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import require_user
from app.models.schemas import DailyTipEnvelope
from app.services.daily_tip_service import DailyTipService
from db import get_db

router = APIRouter(prefix="/daily-tips", tags=["daily_tips"])


@router.get("/", response_model=DailyTipEnvelope)
async def get_daily_tip(
    user: dict = Depends(require_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Fetch today's static styling knowledge tip for the popup entry point.

    This endpoint teaches a transferable styling concept. It does not produce
    a full outfit recommendation; /api/v1/outfit/recommend owns that workflow.
    The generated content is cached per user per day.
    """
    service = DailyTipService(db)
    tip = await service.get_today_tip(user_id=user.get("user_id"))
    return {"code": 200, "data": tip, "msg": "success"}
