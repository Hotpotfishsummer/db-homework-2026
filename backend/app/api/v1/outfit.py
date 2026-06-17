from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import require_user
from app.core.user_llm import apply_user_llm, parse_user_llm_headers
from app.models.schemas import OutfitRecommendRequest
from app.services.styling_agent import StylingAgentService
from db import get_db
from db.repositories.wardrobe_repo import ClothesRepository

router = APIRouter(prefix="/outfit", tags=["outfit"])


@router.post("/recommend")
async def recommend_outfit(
    request: OutfitRecommendRequest,
    http_request: Request,
    user: dict = Depends(require_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Generate an AI outfit recommendation based on scene and user wardrobe.

    The LangChain Agent dynamically queries weather, wardrobe, and user profile
    to produce a contextual recommendation with minimal token usage.

    If the user supplied their own LLM (via X-User-LLM-* headers), the
    agent uses that LLM instead of the server's .env-configured one.
    """
    user_llm = parse_user_llm_headers(http_request)
    agent = StylingAgentService(db)
    with apply_user_llm(user_llm):
        result = await agent.recommend_outfit(
            scene=request.scene,
            wardrobe_ids=request.wardrobeIds,
            user_id=user.get("user_id"),
            location=user.get("location"),
            user_llm=user_llm,
        )

    scene_map = {
        "commute": "通勤",
        "date": "约会",
        "casual": "休闲",
        "sports": "运动",
        "party": "派对",
    }
    result["scene"] = scene_map.get(request.scene, "休闲")

    # Enrich selectedItems: agent only returns int IDs, frontend needs full
    # item details (name/image/category) to render outfit cards. Re-query
    # here to keep the agent's JSON contract clean.
    raw_ids = result.get("selectedItems") or []
    try:
        ids = [int(i) for i in raw_ids if i is not None]
    except (TypeError, ValueError):
        ids = []

    repo = ClothesRepository(db)
    clothes = await repo.get_by_ids(user.get("user_id"), ids, available_only=False)
    by_id = {item.item_id: item for item in clothes}
    result["selectedItems"] = [
        {
            "id": item_id,
            "name": by_id[item_id].name if item_id in by_id else None,
            "image": by_id[item_id].image_url if item_id in by_id else None,
            "category": by_id[item_id].category if item_id in by_id else None,
        }
        for item_id in ids
    ]

    return {"code": 200, "data": result, "msg": "success"}
