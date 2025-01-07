import os
from pydantic import field_validator, ValidationInfo
from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    PROJECT_NAME: str
    DATABASE_USER: str
    DATABASE_PASSWORD: str
    DATABASE_HOST: str
    DATABASE_PORT: int
    DATABASE_NAME: str
    DATABASE_ECHO: bool = True
    ASYNC_DATABASE_URI: str = ""

    @field_validator("ASYNC_DATABASE_URI", mode="after")
    def assemble_db_connection(cls, v: str | None, info: ValidationInfo) -> str:
        if isinstance(v, str) and v == "":
            return f"sqlite+aiosqlite:///{info.data["DATABASE_NAME"]}"
        return v

    class Config:
        env_file = Path(os.path.dirname(__file__)).parent.parent / ".env"


settings = Settings()

if __name__ == "__main__":
    print(settings.ASYNC_DATABASE_URI)
