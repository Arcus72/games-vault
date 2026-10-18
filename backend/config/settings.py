import os
from anyio.functools import lru_cache
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DB_LINK: str
    STEAM_API_KEY: str
    GEMINI_API: str
    MODEL_NAME: str

    class Config:
        env_file = ".env"

@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()