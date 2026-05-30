from sqlalchemy import select, update as sql_update
from sqlalchemy.ext.asyncio import AsyncSession
from db.models.user import User


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self,
        username: str,
        password_hash: str,
        *,
        display_name: str | None = None,
        style_preference: str | None = None,
        location: str | None = None,
    ) -> User:
        user = User(
            username=username,
            password_hash=password_hash,
            display_name=display_name,
            style_preference=style_preference,
            location=location,
        )
        self.session.add(user)
        await self.session.flush()
        return user

    async def get_by_id(self, user_id: int) -> User | None:
        return await self.session.get(User, user_id)

    async def get_by_username(self, username: str) -> User | None:
        stmt = select(User).where(User.username == username)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def update(self, user_id: int, **fields) -> User | None:
        stmt = (
            sql_update(User)
            .where(User.user_id == user_id)
            .values(**fields)
            .returning(User)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def delete(self, user_id: int) -> None:
        user = await self.get_by_id(user_id)
        if user:
            await self.session.delete(user)
            await self.session.flush()

    async def exists(self, user_id: int) -> bool:
        user = await self.get_by_id(user_id)
        return user is not None
