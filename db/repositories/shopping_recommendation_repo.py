from __future__ import annotations

from collections.abc import Iterable
from typing import Any
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from db.models.shopping_recommendation import ShoppingRecommendation


_ALLOWED_STATUSES = {"pending", "bought", "dismissed", "wishlist"}


class ShoppingRecommendationRepository:
    """CRUD + query helpers for AI-recommended shopping items.

    Distinct from `RecommendationRepository` (which manages complete outfit
    recommendations composed of items already in the wardrobe). A shopping
    recommendation is a single *new* item the user might want to buy.
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self,
        user_id: int,
        *,
        name: str,
        category: str,
        color: str | None = None,
        style_tags: list[str] | None = None,
        price_range: str | None = None,
        purchase_url: str | None = None,
        reason: str = "",
        priority: int = 50,
        scene: str | None = None,
        weather_snapshot: dict | None = None,
        status: str = "pending",
    ) -> ShoppingRecommendation:
        rec = ShoppingRecommendation(
            user_id=user_id,
            name=name,
            category=category,
            color=color,
            style_tags=style_tags or [],
            price_range=price_range,
            purchase_url=purchase_url,
            reason=reason,
            priority=priority,
            status=status,
            scene=scene,
            weather_snapshot=weather_snapshot or {},
        )
        self.session.add(rec)
        await self.session.flush()
        return rec

    async def create_batch(
        self,
        user_id: int,
        items: Iterable[dict[str, Any]],
        *,
        scene: str | None = None,
        weather_snapshot: dict | None = None,
    ) -> list[ShoppingRecommendation]:
        results: list[ShoppingRecommendation] = []
        for item in items:
            rec = await self.create(
                user_id=user_id,
                name=item.get("name", "推荐单品"),
                category=item.get("category", "other"),
                color=item.get("color"),
                style_tags=item.get("style_tags") or [],
                price_range=item.get("price_range"),
                purchase_url=item.get("purchase_url"),
                reason=item.get("reason", ""),
                priority=self._coerce_priority(item.get("priority")),
                scene=scene,
                weather_snapshot=weather_snapshot,
                status=item.get("status", "pending"),
            )
            results.append(rec)
        return results

    async def get_by_id(self, user_id: int, recommend_id: UUID) -> ShoppingRecommendation | None:
        stmt = select(ShoppingRecommendation).where(
            ShoppingRecommendation.recommend_id == recommend_id,
            ShoppingRecommendation.user_id == user_id,
        )
        return (await self.session.execute(stmt)).scalar_one_or_none()

    async def list_by_user(
        self,
        user_id: int,
        *,
        status: str | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> list[ShoppingRecommendation]:
        stmt = select(ShoppingRecommendation).where(
            ShoppingRecommendation.user_id == user_id
        )
        if status:
            stmt = stmt.where(ShoppingRecommendation.status == status)
        stmt = (
            stmt.order_by(ShoppingRecommendation.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list((await self.session.execute(stmt)).scalars().all())

    async def update_status(
        self,
        user_id: int,
        recommend_id: UUID,
        status: str,
    ) -> ShoppingRecommendation | None:
        if status not in _ALLOWED_STATUSES:
            raise ValueError(f"Invalid status: {status!r}. Allowed: {sorted(_ALLOWED_STATUSES)}")
        rec = await self.get_by_id(user_id, recommend_id)
        if rec is None:
            return None
        rec.status = status
        from datetime import datetime, timezone
        rec.updated_at = datetime.now(timezone.utc)
        await self.session.flush()
        return rec

    async def delete(self, user_id: int, recommend_id: UUID) -> bool:
        rec = await self.get_by_id(user_id, recommend_id)
        if rec is None:
            return False
        await self.session.delete(rec)
        await self.session.flush()
        return True

    @staticmethod
    def _coerce_priority(value: Any) -> int:
        try:
            p = int(value) if value is not None else 50
        except (TypeError, ValueError):
            return 50
        return max(0, min(100, p))
