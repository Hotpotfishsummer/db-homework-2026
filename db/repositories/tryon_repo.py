from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from db.models.tryon_result import TryonResult


class TryonRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, user_id: int, base_image_url: str,
                     result_image_url: str) -> TryonResult:
        tr = TryonResult(user_id=user_id, base_image_url=base_image_url,
                         result_image_url=result_image_url)
        self.session.add(tr)
        await self.session.flush()
        return tr

    async def get_by_id(self, tryon_id: int) -> TryonResult | None:
        return await self.session.get(TryonResult, tryon_id)

    async def list_by_user(self, user_id: int, *, limit: int = 20,
                           offset: int = 0) -> list[TryonResult]:
        stmt = (
            select(TryonResult)
            .where(TryonResult.user_id == user_id)
            .order_by(TryonResult.created_at.desc())
            .limit(limit).offset(offset)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def delete(self, tryon_id: int) -> tuple[str, str] | None:
        tr = await self.get_by_id(tryon_id)
        if tr:
            base, result = tr.base_image_url, tr.result_image_url
            await self.session.delete(tr)
            await self.session.flush()
            return base, result
        return None
