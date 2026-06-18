from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import require_user
from app.core.user_llm import apply_user_llm, parse_user_llm_headers
from app.models.schemas import OutfitRecommendRequest
from app.services.styling_agent import StylingAgentService
from db import get_db
from db.models.recommendation import OutfitRecommendation
from db.repositories.activity_repo import FavoriteRepository
from db.repositories.recommendation_repo import RecommendationRepository
from db.repositories.wardrobe_repo import ClothesRepository

router = APIRouter(prefix="/outfit", tags=["outfit"])


SCENE_MAP = {
    "commute": "通勤",
    "date": "约会",
    "casual": "休闲",
    "sports": "运动",
    "party": "派对",
}


def _serialize_recommendation(rec: OutfitRecommendation, favorited_at=None) -> dict:
    selected_items = []
    for rec_item in sorted(rec.items or [], key=lambda item: item.sort_order):
        snapshot = rec_item.item_snapshot or {}
        selected_items.append(
            {
                "id": rec_item.item_id,
                "name": snapshot.get("name"),
                "image": snapshot.get("image_url"),
                "category": snapshot.get("category") or rec_item.slot,
            }
        )

    content = rec.content or ""
    data = {
        "id": str(rec.recommend_id),
        "outfitId": str(rec.recommend_id),
        "recommendId": str(rec.recommend_id),
        "scene": SCENE_MAP.get(rec.scene, rec.scene),
        "name": rec.title,
        "description": content,
        "reason": content,
        "matchRate": rec.match_rate,
        "image": rec.image_url or "",
        "selectedItems": selected_items,
        "weatherSummary": rec.weather_snapshot.get("summary", "") if rec.weather_snapshot else "",
        "generatedBy": "database",
        "createdAt": rec.created_at.isoformat() if rec.created_at else None,
    }
    if favorited_at:
        data["likedAt"] = favorited_at.isoformat()
    return data


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
            body_profile=request.bodyProfile,
        )

    # Enrich selectedItems: agent only returns int IDs, frontend needs full
    # item details (name/image/category) to render outfit cards. Re-query
    # here to keep the agent's JSON contract clean.
    raw_ids = result.get("selectedItems") or []
    try:
        ids = [int(i) for i in raw_ids if i is not None]
    except (TypeError, ValueError):
        ids = []

    if not ids:
        ids = [int(i) for i in (request.wardrobeIds or []) if i is not None]

    repo = ClothesRepository(db)
    clothes = await repo.get_by_ids(user.get("user_id"), ids, available_only=False)
    by_id = {item.item_id: item for item in clothes}
    if not result.get("selectedItems") and clothes:
        result["generatedBy"] = "fallback"
        result["selectedItems"] = [item.item_id for item in clothes]
        result["name"] = result.get("name") or "衣橱基础搭配"
        result["description"] = result.get("description") or "根据你当前选择的衣橱单品生成的基础搭配"
        result["reason"] = result.get("reason") or "AI 输出格式异常，已使用你本次选择的真实衣橱单品生成可查看的基础搭配。"

    result["selectedItems"] = [
        {
            "id": item_id,
            "name": by_id[item_id].name if item_id in by_id else None,
            "image": by_id[item_id].image_url if item_id in by_id else None,
            "category": by_id[item_id].category if item_id in by_id else None,
        }
        for item_id in ids
        if item_id in by_id
    ]
    stored_rec = await RecommendationRepository(db).create(
        user_id=user.get("user_id"),
        scene=request.scene,
        title=result.get("name") or "AI 穿搭方案",
        description=result.get("description") or "",
        reason=result.get("reason") or "",
        match_rate=result.get("matchRate") or 0,
        image_url=result.get("image") or None,
        weather_snapshot={"summary": result.get("weatherSummary") or ""},
        items=[by_id[item_id] for item_id in ids if item_id in by_id],
    )
    result["id"] = str(stored_rec.recommend_id)
    result["outfitId"] = str(stored_rec.recommend_id)
    result["recommendId"] = str(stored_rec.recommend_id)
    result["scene"] = SCENE_MAP.get(request.scene, "休闲")

    return {"code": 200, "data": result, "msg": "success"}


@router.get("/favorites")
async def list_favorite_outfits(
    user: dict = Depends(require_user),
    db: AsyncSession = Depends(get_db),
):
    favorites = await FavoriteRepository(db).list_by_user(user.get("user_id"), limit=100)
    return {
        "code": 200,
        "data": [
            _serialize_recommendation(favorite.recommendation, favorite.favorited_at)
            for favorite in favorites
            if favorite.recommendation
        ],
        "msg": "success",
    }


@router.post("/favorites/{recommend_id}")
async def favorite_outfit(
    recommend_id: UUID,
    user: dict = Depends(require_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        await FavoriteRepository(db).add(user.get("user_id"), recommend_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    rec = await RecommendationRepository(db).get_by_id(user.get("user_id"), recommend_id)
    return {
        "code": 200,
        "data": _serialize_recommendation(rec) if rec else {"id": str(recommend_id)},
        "msg": "success",
    }


@router.delete("/favorites/{recommend_id}")
async def unfavorite_outfit(
    recommend_id: UUID,
    user: dict = Depends(require_user),
    db: AsyncSession = Depends(get_db),
):
    await FavoriteRepository(db).remove(user.get("user_id"), recommend_id)
    return {"code": 200, "data": {"id": str(recommend_id)}, "msg": "success"}
