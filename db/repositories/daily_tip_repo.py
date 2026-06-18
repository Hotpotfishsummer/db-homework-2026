from __future__ import annotations

from datetime import date

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from db.models.daily_tip import DailyTip


class DailyTipRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_for_date(
        self,
        user_id: int,
        tip_date: date,
        *,
        tip_type: str | None = None,
    ) -> DailyTip | None:
        stmt = select(DailyTip).where(DailyTip.user_id == user_id, DailyTip.tip_date == tip_date)
        if tip_type is not None:
            stmt = stmt.where(DailyTip.tip_type == tip_type)
        return (await self.session.execute(stmt)).scalar_one_or_none()

    async def get_today(self, user_id: int, *, tip_type: str | None = None) -> DailyTip | None:
        return await self.get_for_date(user_id, date.today(), tip_type=tip_type)

    async def create_or_get(
        self,
        user_id: int,
        *,
        content: str,
        tip_date: date | None = None,
        tip_type: str = "outfit",
    ) -> DailyTip:
        target_date = tip_date or date.today()
        stmt = (
            insert(DailyTip)
            .values(
                user_id=user_id,
                tip_date=target_date,
                tip_type=tip_type,
                content=content,
            )
            .on_conflict_do_nothing(index_elements=[DailyTip.user_id, DailyTip.tip_date])
            .returning(DailyTip)
        )
        created = (await self.session.execute(stmt)).scalar_one_or_none()
        if created is not None:
            return created
        existing = await self.get_for_date(user_id, target_date, tip_type=tip_type)
        if existing is None:
            existing = await self.get_for_date(user_id, target_date)
        if existing is None:
            raise RuntimeError("Daily tip insert conflicted but existing record was not found")
        return existing

    async def list_by_user(
        self, user_id: int, *, limit: int = 30, offset: int = 0
    ) -> list[DailyTip]:
        stmt = (
            select(DailyTip)
            .where(DailyTip.user_id == user_id)
            .order_by(DailyTip.tip_date.desc())
            .limit(limit)
            .offset(offset)
        )
        return list((await self.session.execute(stmt)).scalars().all())
