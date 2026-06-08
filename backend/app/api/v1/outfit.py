from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import require_user
from app.models.schemas import OutfitRecommendRequest
from app.services.styling_agent import StylingAgentService
from db import get_db

router = APIRouter(prefix="/outfit", tags=["outfit"])


@router.post("/recommend")
async def recommend_outfit(
    request: OutfitRecommendRequest,
    user: dict = Depends(require_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Generate an AI outfit recommendation based on scene and user wardrobe.

    The LangChain Agent dynamically queries weather, wardrobe, and user profile
    to produce a contextual recommendation with minimal token usage.
    """
    agent = StylingAgentService(db)
    result = await agent.recommend_outfit(
        scene=request.scene,
        wardrobe_ids=request.wardrobeIds,
        user_id=user.get("user_id"),
        location=user.get("location"),
    )

    scene_map = {
        "commute": "通勤",
        "date": "约会",
        "casual": "休闲",
        "sports": "运动",
        "party": "派对",
    }
    result["scene"] = scene_map.get(request.scene, "休闲")

    return {"code": 200, "data": result, "msg": "success"}
