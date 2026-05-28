from fastapi import APIRouter, Depends
from app.core.security import require_user
from app.models.schemas import OutfitRecommendRequest, StylingRecommendationEnvelope
from app.services.styling_agent import StylingAgentService

router = APIRouter(prefix="/outfit", tags=["outfit"])
styling_agent = StylingAgentService()


@router.post("/recommend", response_model=StylingRecommendationEnvelope)
async def recommend_outfit(
    request: OutfitRecommendRequest,
    user: dict = Depends(require_user),
):
    """
    根据场景和用户衣橱生成 AI 穿搭推荐。

    由 StylingAgentService 统一负责天气、衣橱和 agent 编排。
    """
    result = await styling_agent.recommend_outfit(
        scene=request.scene,
        wardrobe_ids=request.wardrobeIds,
        user_id=user.get("user_id"),
        location=user.get("location"),
    )

    # 场景中文映射（与前端对齐）
    scene_map = {
        "commute": "通勤",
        "date": "约会",
        "casual": "休闲",
        "sports": "运动",
        "party": "派对",
    }
    result["scene"] = scene_map.get(request.scene, "休闲")

    return {"code": 200, "data": result, "msg": "success"}
