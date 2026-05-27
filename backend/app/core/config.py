from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "L-Wardrobe"
    debug: bool = False
    secret_key: str = "change-me"

    weather_api_key: str = ""
    hefeng_api_key: str = ""
    hefeng_api_host: str = ""
    deepseek_api_key: str = ""
    llm_api_key: str = ""
    llm_api_base: str = "https://api.openai.com/v1"
    database_url: str = "postgresql+asyncpg://postgres:postgres@127.0.0.1:5432/l_wardrobe"

    class Config:
        env_file = str(Path(__file__).resolve().parents[2] / ".env")
        env_file_encoding = "utf-8"


@lru_cache
def get_settings() -> Settings:
    return Settings()
