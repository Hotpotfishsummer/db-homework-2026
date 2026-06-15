"""AI Recommendation API endpoints (新购单品 + 嵌入搭配 + 缺口分析).

Distinct from /api/v1/outfit/* which handles the wardrobe-internal outfit
recommendation flow. See docs/architecture/overview.md for the dual-track
design rationale.
"""

from __future__ import annotations

import logging
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import require_user
from app.models.schemas import (
    ItemRecommendEnvelope,
    ItemRecommendRequest,
    ItemStatusUpdate,
    ShoppingOutfitEnvelope,
    ShoppingOutfitRequest,
    WardrobeGapEnvelope,
)
from app.services.recommendation_agent import RecommendationAgentService
from db import get_db
from db.repositories.shopping_recommendation_repo import ShoppingRecommendationRepository

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/recommend", tags=["recommendation"])


# ------------------------------------------------------------------
# POST /api/v1/recommend/items — recommend new shopping items
# ------------------------------------------------------------------
@router.post("/items", response_model=ItemRecommendEnvelope)
async def recommend_items(
    request: ItemRecommendRequest,
    user: dict = Depends(require_user),
    db: AsyncSession = Depends(get_db),
):
    """Recommend 5-8 new items the user might want to buy."""
    agent = RecommendationAgentService(db)
    result = await agent.recommend_items(
        scene=request.scene,
        user_id=user.get("user_id"),
        location=user.get("location"),
        gap_focus=request.gapFocus,
    )
    # The persistence step inside recommend_items already committed; refresh
    # each persisted item so we return its DB-assigned id.
    items = result.get("items", [])
    persisted = []
    repo = ShoppingRecommendationRepository(db)
    for item in items:
        # Find the most recent row matching this name+category+scene to get the
        # DB-assigned UUID. This is the simplest reliable correlation since
        # the LLM doesn't return the id back into the JSON.
        rows = await repo.list_by_user(
            user.get("user_id"), status="pending", limit=10,
        )
        match = next(
            (r for r in rows
             if r.name == item["name"] and r.category == item["category"]),
            None,
        )
        persisted.append(
            {
                **item,
                "id": str(match.recommend_id) if match else None,
            }
        )
    return {
        "code": 200,
        "data": {
            **result,
            "items": persisted,
        },
        "msg": "success",
    }


# ------------------------------------------------------------------
# GET /api/v1/recommend/items — list history
# ------------------------------------------------------------------
@router.get("/items")
async def list_recommended_items(
    status_filter: str = Query("pending", alias="status"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    user: dict = Depends(require_user),
    db: AsyncSession = Depends(get_db),
):
    """List current user's recommended items, newest first."""
    repo = ShoppingRecommendationRepository(db)
    items = await repo.list_by_user(
        user.get("user_id"),
        status=status_filter if status_filter != "all" else None,
        limit=limit,
        offset=offset,
    )
    return {
        "code": 200,
        "data": {
            "items": [
                {
                    "id": str(r.recommend_id),
                    "name": r.name,
                    "category": r.category,
                    "color": r.color,
                    "style_tags": r.style_tags,
                    "price_range": r.price_range,
                    "purchase_url": r.purchase_url,
                    "reason": r.reason,
                    "priority": r.priority,
                    "status": r.status,
                    "scene": r.scene,
                    "created_at": r.created_at.isoformat() if r.created_at else None,
                }
                for r in items
            ],
            "limit": limit,
            "offset": offset,
        },
        "msg": "success",
    }


# ------------------------------------------------------------------
# PATCH /api/v1/recommend/items/{id} — update status
# ------------------------------------------------------------------
@router.patch("/items/{item_id}")
async def update_recommended_item_status(
    item_id: str,
    body: ItemStatusUpdate,
    user: dict = Depends(require_user),
    db: AsyncSession = Depends(get_db),
):
    """Mark a recommended item as bought / dismissed / wishlist."""
    try:
        parsed_id = UUID(item_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid item id (must be UUID)")

    repo = ShoppingRecommendationRepository(db)
    try:
        updated = await repo.update_status(user.get("user_id"), parsed_id, body.status)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    await db.commit()
    if updated is None:
        raise HTTPException(status_code=404, detail="Item not found or not owned by user")
    return {
        "code": 200,
        "data": {
            "id": str(updated.recommend_id),
            "status": updated.status,
        },
        "msg": "success",
    }


# ------------------------------------------------------------------
# POST /api/v1/recommend/items/with-outfit — embed new items into outfit
# ------------------------------------------------------------------
@router.post("/items/with-outfit", response_model=ShoppingOutfitEnvelope)
async def recommend_shopping_outfit(
    request: ShoppingOutfitRequest,
    user: dict = Depends(require_user),
    db: AsyncSession = Depends(get_db),
):
    """Produce a 4-5 slot outfit mixing owned + recommended items."""
    agent = RecommendationAgentService(db)
    result = await agent.recommend_with_wardrobe(
        scene=request.scene,
        user_id=user.get("user_id"),
        location=user.get("location"),
    )
    return {"code": 200, "data": result, "msg": "success"}


# ------------------------------------------------------------------
# POST /api/v1/recommend/gap-analysis — wardrobe gap report
# ------------------------------------------------------------------
@router.post("/gap-analysis", response_model=WardrobeGapEnvelope)
async def gap_analysis(
    user: dict = Depends(require_user),
    db: AsyncSession = Depends(get_db),
):
    """Analyze category-level gaps in the user's wardrobe."""
    agent = RecommendationAgentService(db)
    result = await agent.analyze_wardrobe_gap(
        user_id=user.get("user_id"),
        location=user.get("location"),
    )
    return {"code": 200, "data": result, "msg": "success"}
