import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DB_LINK: str

    class Config:
        env_file = ".env"
