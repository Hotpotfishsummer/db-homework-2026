from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from db.models.wardrobe_item import Clothes


class ClothesRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self,
        user_id: int,
        image_url: str,
        category: str | None = None,
        attributes: dict | None = None,
        *,
        name: str | None = None,
        color: str | None = None,
        seasons: list[str] | None = None,
        status: str = "available",
    ) -> Clothes:
        attributes = dict(attributes or {})
        ai_tags = attributes.get("tags") if isinstance(attributes.get("tags"), dict) else {}
        resolved_category = category or ai_tags.get("category") or "other"
        resolved_color = color if color is not None else attributes.get("color", ai_tags.get("color"))
        resolved_seasons = seasons if seasons is not None else attributes.get("seasons", ai_tags.get("season", []))
        attributes.setdefault("color", resolved_color)
        attributes.setdefault("seasons", resolved_seasons)
        attributes.setdefault("status", status)
        item = Clothes(
            user_id=user_id,
            name=name or attributes.get("name") or attributes.get("source_filename") or "未命名单品",
            image_url=image_url,
            category=resolved_category,
            color=resolved_color,
            seasons=resolved_seasons,
            status=status,
            attributes=attributes,
        )
        self.session.add(item)
        await self.session.flush()
        return item

    async def get_by_id(self, user_id: int, item_id: int, *, include_deleted: bool = False) -> Clothes | None:
        stmt = select(Clothes).where(Clothes.user_id == user_id, Clothes.item_id == item_id)
        if not include_deleted:
            stmt = stmt.where(Clothes.deleted_at.is_(None))
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_ids(
        self, user_id: int, ids: list[int], *, available_only: bool = True
    ) -> list[Clothes]:
        if not ids:
            return []
        stmt = (
            select(Clothes)
            .where(Clothes.user_id == user_id)
            .where(Clothes.item_id.in_(ids))
            .where(Clothes.deleted_at.is_(None))
        )
        if available_only:
            stmt = stmt.where(Clothes.status == "available")
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def list_by_user(self, user_id: int, *, category: str | None = None,
                           season: str | None = None, color: str | None = None,
                           status: str | None = None,
                           limit: int = 20, offset: int = 0) -> list[Clothes]:
        stmt = select(Clothes).where(Clothes.user_id == user_id, Clothes.deleted_at.is_(None))
        if category:
            stmt = stmt.where(Clothes.category == category)
        if season:
            stmt = stmt.where(Clothes.seasons.contains([season]))
        if color:
            stmt = stmt.where(Clothes.color == color)
        if status:
            stmt = stmt.where(Clothes.status == status)
        stmt = stmt.order_by(Clothes.created_at.desc()).limit(limit).offset(offset)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def update(self, user_id: int, item_id: int, **fields) -> Clothes | None:
        allowed_fields = {"name", "category", "color", "seasons", "status", "attributes", "image_url"}
        unknown_fields = set(fields) - allowed_fields
        if unknown_fields:
            raise ValueError(f"Unsupported clothes fields: {sorted(unknown_fields)}")
        item = await self.get_by_id(user_id, item_id)
        if item is None:
            return None
        mirrored_attributes = dict(item.attributes)
        for field, value in fields.items():
            setattr(item, field, value)
            if field in {"color", "seasons", "status"}:
                mirrored_attributes[field] = value
        item.attributes = mirrored_attributes
        await self.session.flush()
        return item

    async def get_image_path(self, user_id: int, item_id: int) -> str | None:
        item = await self.get_by_id(user_id, item_id)
        return item.image_url if item else None

    async def delete(self, user_id: int, item_id: int) -> str | None:
        """Soft-delete an item and return its image URL for optional cleanup."""
        item = await self.get_by_id(user_id, item_id)
        if item:
            path = item.image_url
            item.deleted_at = datetime.now(timezone.utc)
            await self.session.flush()
            return path
        return None

    async def count_by_user(self, user_id: int) -> int:
        stmt = select(func.count()).where(Clothes.user_id == user_id, Clothes.deleted_at.is_(None))
        result = await self.session.execute(stmt)
        return result.scalar_one()


WardrobeRepository = ClothesRepository
