from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    app_name: str = "L-Wardrobe"
    debug: bool = False
    secret_key: str = "change-me"

    weather_api_key: str = ""
    llm_api_key: str = ""
    llm_api_base: str = "https://api.openai.com/v1"
    database_url: str = "sqlite:///./wardrobe.db"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache
def get_settings() -> Settings:
    return Settings()
