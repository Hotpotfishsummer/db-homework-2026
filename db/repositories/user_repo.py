from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from db.models.user import User
from db.models.user_profile import UserProfile


PROFILE_FIELDS = {
    "display_name",
    "avatar_url",
    "bio",
    "location",
    "skin_tone",
    "body_shape",
    "preferences",
    "style_preference",
    "style_axes",
    "style_tags",
    "favorite_colors",
    "avoid_colors",
    "fit_preference",
}
ACCOUNT_FIELDS = {"username", "password_hash"}
PREFERENCE_FIELDS = {
    "style_preference",
    "style_axes",
    "style_tags",
    "favorite_colors",
    "avoid_colors",
    "fit_preference",
}


def _apply_profile_fields(profile: UserProfile, fields: dict) -> None:
    for field, value in fields.items():
        if field == "preferences":
            profile.preferences = dict(value or {})
            continue
        if field in PREFERENCE_FIELDS:
            setattr(profile, field, value)
            continue
        setattr(profile, field, value)


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
            profile=UserProfile(
                display_name=display_name,
                location=location,
            ),
        )
        if style_preference is not None:
            user.profile.style_preference = style_preference
        self.session.add(user)
        await self.session.flush()
        return user

    async def get_by_id(self, user_id: int) -> User | None:
        stmt = select(User).options(selectinload(User.profile)).where(User.user_id == user_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_username(self, username: str) -> User | None:
        stmt = select(User).options(selectinload(User.profile)).where(User.username == username)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def update(self, user_id: int, **fields) -> User | None:
        unknown_fields = set(fields) - ACCOUNT_FIELDS - PROFILE_FIELDS
        if unknown_fields:
            raise ValueError(f"Unsupported user fields: {sorted(unknown_fields)}")

        user = await self.get_by_id(user_id)
        if user is None:
            return None

        for field in ACCOUNT_FIELDS:
            if field in fields:
                setattr(user, field, fields[field])

        profile = user._ensure_profile()
        _apply_profile_fields(profile, fields)

        await self.session.flush()
        return user

    async def delete(self, user_id: int) -> None:
        user = await self.get_by_id(user_id)
        if user:
            await self.session.delete(user)
            await self.session.flush()

    async def exists(self, user_id: int) -> bool:
        user = await self.get_by_id(user_id)
        return user is not None


class UserProfileRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_user_id(self, user_id: int) -> UserProfile | None:
        return await self.session.get(UserProfile, user_id)

    async def get_or_create(self, user_id: int) -> UserProfile:
        profile = await self.get_by_user_id(user_id)
        if profile is None:
            profile = UserProfile(user_id=user_id)
            self.session.add(profile)
            await self.session.flush()
        return profile

    async def update(self, user_id: int, **fields) -> UserProfile:
        unknown_fields = set(fields) - PROFILE_FIELDS
        if unknown_fields:
            raise ValueError(f"Unsupported profile fields: {sorted(unknown_fields)}")

        profile = await self.get_or_create(user_id)
        _apply_profile_fields(profile, fields)
        await self.session.flush()
        return profile
