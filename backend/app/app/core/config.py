import os
from pydantic import field_validator, ValidationInfo
from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    VIRTUAL_HOST: str
    DEFAULT_HOST: str
    PROJECT_NAME: str
    DATABASE_USER: str
    DATABASE_PASSWORD: str
    DATABASE_HOST: str
    DATABASE_PORT: int
    DATABASE_ECHO: bool = True
    DATABASE_VOLUME: str
    ASYNC_DATABASE_URI: str = "sqlite+aiosqlite:////app/app/db/.sqlite3"

    class Config:
        env_file = Path(os.path.dirname(__file__)).parent.parent / ".env"


settings = Settings()

if __name__ == "__main__":
    print(settings.ASYNC_DATABASE_URI)
