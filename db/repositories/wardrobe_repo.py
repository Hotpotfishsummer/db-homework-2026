from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from db.models.wardrobe_item import Clothes


class ClothesRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, user_id: int, image_url: str, category: str | None = None,
                     attributes: dict | None = None) -> Clothes:
        item = Clothes(user_id=user_id, image_url=image_url,
                       category=category, attributes=attributes)
        self.session.add(item)
        await self.session.flush()
        return item

    async def get_by_id(self, item_id: int) -> Clothes | None:
        return await self.session.get(Clothes, item_id)

    async def get_by_ids(self, user_id: int, ids: list[int]) -> list[Clothes]:
        stmt = (
            select(Clothes)
            .where(Clothes.user_id == user_id)
            .where(Clothes.item_id.in_(ids))
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def list_by_user(self, user_id: int, *, category: str | None = None,
                           season: str | None = None, color: str | None = None,
                           limit: int = 20, offset: int = 0) -> list[Clothes]:
        stmt = select(Clothes).where(Clothes.user_id == user_id)
        if category:
            stmt = stmt.where(Clothes.category == category)
        if season:
            stmt = stmt.where(Clothes.attributes.contains({"season": season}))
        if color:
            stmt = stmt.where(Clothes.attributes.contains({"color": color}))
        stmt = stmt.order_by(Clothes.created_at.desc()).limit(limit).offset(offset)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_image_path(self, item_id: int) -> str | None:
        item = await self.get_by_id(item_id)
        return item.image_url if item else None

    async def delete(self, item_id: int) -> str | None:
        item = await self.get_by_id(item_id)
        if item:
            path = item.image_url
            await self.session.delete(item)
            await self.session.flush()
            return path
        return None

    async def count_by_user(self, user_id: int) -> int:
        stmt = select(func.count()).where(Clothes.user_id == user_id)
        result = await self.session.execute(stmt)
        return result.scalar_one()


WardrobeRepository = ClothesRepository
