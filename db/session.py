from pathlib import Path
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from pydantic_settings import BaseSettings
from typing import AsyncGenerator


class DBConfig(BaseSettings):
    database_url: str
    model_config = {"env_file": str(Path(__file__).parent / ".env"), "env_file_encoding": "utf-8"}


_config = DBConfig()


def _build_async_url(raw: str) -> str:
    """Convert a PostgreSQL URL to asyncpg-compatible format."""
    if raw.startswith("postgresql://"):
        raw = raw.replace("postgresql://", "postgresql+asyncpg://", 1)
    elif raw.startswith("postgres://"):
        raw = raw.replace("postgres://", "postgresql+asyncpg://", 1)
    if "sslmode=require" in raw:
        raw = raw.replace("sslmode=require", "ssl=require")
    if "&channel_binding=require" in raw:
        raw = raw.replace("&channel_binding=require", "")
    return raw


_raw_url = _build_async_url(_config.database_url)

async_engine = create_async_engine(
    _raw_url,
    pool_size=10,
    max_overflow=5,
    echo=False,
)

async_session = async_sessionmaker(async_engine, expire_on_commit=False)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
