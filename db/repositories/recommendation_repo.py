from __future__ import annotations

from collections.abc import Iterable
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from db.models.recommendation import OutfitRecommendation, RecommendationItem
from db.models.wardrobe_item import Clothes


class RecommendationRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self,
        user_id: int,
        scene: str,
        *,
        title: str,
        content: str | None = None,
        description: str = "",
        reason: str = "",
        match_rate: int = 0,
        image_url: str | None = None,
        weather_snapshot: dict | None = None,
        items: Iterable[Clothes | dict[str, Any]] = (),
    ) -> OutfitRecommendation:
        normalized_content = content if content is not None else self._merge_content(description, reason)
        recommendation = OutfitRecommendation(
            user_id=user_id,
            scene=scene,
            weather_snapshot=weather_snapshot or {},
            title=title,
            content=normalized_content,
            match_rate=self._normalize_match_rate(match_rate),
            image_url=image_url,
        )
        for item_order, selected in enumerate(items):
            item, slot = self._coerce_selected_item(selected)
            if item.user_id != user_id:
                raise ValueError("Recommendation item does not belong to user")
            recommendation.items.append(
                RecommendationItem(
                    item=item,
                    slot=slot or item.category,
                    sort_order=item_order,
                    item_snapshot={
                        "name": item.name,
                        "category": item.category,
                        "image_url": item.image_url,
                        "color": item.color,
                    },
                )
            )
        self.session.add(recommendation)
        await self.session.flush()
        return recommendation

    async def create_many(
        self,
        user_id: int,
        scene: str,
        recommendations: list[dict[str, Any]],
        *,
        weather_snapshot: dict | None = None,
    ) -> list[OutfitRecommendation]:
        stored = []
        for data in recommendations:
            stored.append(
                await self.create(
                    user_id,
                    scene,
                    title=data["title"],
                    content=data.get("content"),
                    description=data.get("description", ""),
                    reason=data.get("reason", ""),
                    match_rate=data.get("match_rate", data.get("matchRate", 0)),
                    image_url=data.get("image_url"),
                    weather_snapshot=weather_snapshot,
                    items=data.get("items", ()),
                )
            )
        return stored

    async def get_by_id(self, user_id: int, recommend_id: UUID) -> OutfitRecommendation | None:
        stmt = (
            select(OutfitRecommendation)
            .options(selectinload(OutfitRecommendation.items))
            .where(
                OutfitRecommendation.user_id == user_id,
                OutfitRecommendation.recommend_id == recommend_id,
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_user(
        self, user_id: int, *, limit: int = 20, offset: int = 0
    ) -> list[OutfitRecommendation]:
        stmt = (
            select(OutfitRecommendation)
            .options(selectinload(OutfitRecommendation.items))
            .where(OutfitRecommendation.user_id == user_id)
            .order_by(OutfitRecommendation.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    def _coerce_selected_item(selected: Clothes | dict[str, Any]) -> tuple[Clothes, str | None]:
        if isinstance(selected, Clothes):
            return selected, None
        item = selected.get("item")
        if not isinstance(item, Clothes):
            raise TypeError("Recommendation item mappings must contain a Clothes instance")
        return item, selected.get("slot")

    @staticmethod
    def _merge_content(description: str, reason: str) -> str:
        parts = [part.strip() for part in (description, reason) if part and part.strip()]
        return "\n\n".join(parts)

    @staticmethod
    def _normalize_match_rate(value: Any) -> int:
        try:
            rate = int(value)
        except (TypeError, ValueError):
            return 0
        return max(0, min(rate, 100))
