from alembic import context
from sqlalchemy.ext.asyncio import create_async_engine
from db.base import Base
from db.models import (
    User, UserProfile, Clothes, WardrobeItem,
    OutfitRecommendation, RecommendationItem,
    OutfitFavorite, OutfitHistory, DailyTip,
)
from db.session import _config, _build_async_url

target_metadata = Base.metadata


def get_url():
    return _build_async_url(_config.database_url)


def run_migrations_offline():
    context.configure(url=get_url(), target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online():
    engine = create_async_engine(get_url())
    async with engine.connect() as conn:
        await conn.run_sync(_do_run_migrations)
    await engine.dispose()


def _do_run_migrations(connection):
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    import asyncio
    asyncio.run(run_migrations_online())
