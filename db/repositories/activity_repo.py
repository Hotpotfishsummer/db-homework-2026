from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from db.models.outfit_activity import OutfitFavorite, OutfitHistory
from db.models.recommendation import OutfitRecommendation


def _utcnow():
    return datetime.now(timezone.utc)


async def _require_owned_recommendation(
    session: AsyncSession, user_id: int, recommend_id: UUID
) -> None:
    stmt = select(OutfitRecommendation.recommend_id).where(
        OutfitRecommendation.recommend_id == recommend_id,
        OutfitRecommendation.user_id == user_id,
    )
    if (await session.execute(stmt)).scalar_one_or_none() is None:
        raise ValueError("Recommendation does not belong to user")


class FavoriteRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add(self, user_id: int, recommend_id: UUID) -> None:
        await _require_owned_recommendation(self.session, user_id, recommend_id)
        stmt = insert(OutfitFavorite).values(user_id=user_id, recommend_id=recommend_id)
        await self.session.execute(stmt.on_conflict_do_nothing())

    async def remove(self, user_id: int, recommend_id: UUID) -> None:
        stmt = delete(OutfitFavorite).where(
            OutfitFavorite.user_id == user_id,
            OutfitFavorite.recommend_id == recommend_id,
        )
        await self.session.execute(stmt)

    async def list_by_user(
        self, user_id: int, *, limit: int = 20, offset: int = 0
    ) -> list[OutfitFavorite]:
        stmt = (
            select(OutfitFavorite)
            .options(
                selectinload(OutfitFavorite.recommendation).selectinload(OutfitRecommendation.items)
            )
            .where(OutfitFavorite.user_id == user_id)
            .order_by(OutfitFavorite.favorited_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list((await self.session.execute(stmt)).scalars().all())


class HistoryRepository:
    ACTIONS = {"detail", "liked", "skipped"}

    def __init__(self, session: AsyncSession):
        self.session = session

    async def record_action(self, user_id: int, recommend_id: UUID, action: str) -> None:
        if action not in self.ACTIONS:
            raise ValueError(f"Unsupported history action: {action}")
        await _require_owned_recommendation(self.session, user_id, recommend_id)
        now = _utcnow()
        stmt = insert(OutfitHistory).values(
            user_id=user_id,
            recommend_id=recommend_id,
            first_viewed_at=now,
            last_viewed_at=now,
            view_count=1,
            last_action=action,
        )
        await self.session.execute(
            stmt.on_conflict_do_update(
                index_elements=[OutfitHistory.user_id, OutfitHistory.recommend_id],
                set_={
                    "last_viewed_at": now,
                    "view_count": OutfitHistory.view_count + 1,
                    "last_action": action,
                },
            )
        )

    async def list_by_user(
        self, user_id: int, *, limit: int = 50, offset: int = 0
    ) -> list[OutfitHistory]:
        stmt = (
            select(OutfitHistory)
            .options(
                selectinload(OutfitHistory.recommendation).selectinload(OutfitRecommendation.items)
            )
            .where(OutfitHistory.user_id == user_id)
            .order_by(OutfitHistory.last_viewed_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list((await self.session.execute(stmt)).scalars().all())

    async def clear(self, user_id: int) -> None:
        await self.session.execute(delete(OutfitHistory).where(OutfitHistory.user_id == user_id))
