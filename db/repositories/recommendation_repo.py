from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from db.models.outfit_recommendation import OutfitRecommendation


class RecommendationRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, user_id: int, weather_context: dict | None,
                     analysis_doc: str, selected_items: list | None = None) -> OutfitRecommendation:
        rec = OutfitRecommendation(
            user_id=user_id, weather_context=weather_context,
            analysis_doc=analysis_doc, selected_items=selected_items,
        )
        self.session.add(rec)
        await self.session.flush()
        return rec

    async def get_by_id(self, rec_id: int) -> OutfitRecommendation | None:
        return await self.session.get(OutfitRecommendation, rec_id)

    async def list_by_user(self, user_id: int, *, limit: int = 20,
                           offset: int = 0) -> list[OutfitRecommendation]:
        stmt = (
            select(OutfitRecommendation)
            .where(OutfitRecommendation.user_id == user_id)
            .order_by(OutfitRecommendation.created_at.desc())
            .limit(limit).offset(offset)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def delete(self, rec_id: int) -> None:
        rec = await self.get_by_id(rec_id)
        if rec:
            await self.session.delete(rec)
            await self.session.flush()
