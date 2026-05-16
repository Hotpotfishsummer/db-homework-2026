from fastapi import APIRouter, Depends
from app.core.security import require_user
from app.services.weather import WeatherService
from app.services.outfit_ai import OutfitAIService
from app.services.wardrobe_stub import WardrobeService
from app.models.schemas import OutfitRecommendRequest

router = APIRouter(prefix="/outfit", tags=["outfit"])
weather_svc = WeatherService()
ai_svc = OutfitAIService()
wardrobe_svc = WardrobeService()


@router.post("/recommend")
async def recommend_outfit(
    request: OutfitRecommendRequest,
    user: dict = Depends(require_user),
):
    """
    根据场景和用户衣橱生成 AI 穿搭推荐。

    TODO: 衣橱查询待接入数据库（目前用 WardrobeService stub）。
    TODO: 用户 location 待接入数据库（目前默认"北京"）。
    """
    # 1. 查询衣橱（stub）
    clothes = await wardrobe_svc.get_by_ids(user["user_id"], request.wardrobeIds)

    # 2. 查询天气（TODO: location 从用户 profile 取）
    weather = await weather_svc.get_current(location="深圳")

    # 3. AI 推荐
    result = await ai_svc.recommend(request.scene, clothes, weather)

    # 4. 场景中文映射（与前端对齐）
    scene_map = {
        "commute": "通勤",
        "date": "约会",
        "casual": "休闲",
        "sports": "运动",
        "party": "派对",
    }
    result["scene"] = scene_map.get(request.scene, "休闲")

    return {"code": 200, "data": result, "msg": "success"}
