from datetime import timedelta
from pathlib import Path
from dotenv import load_dotenv
from pydantic import field_validator, PostgresDsn, ValidationInfo
from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).parent.parent.parent.parent
ENV_PATH = BASE_DIR / "user_service" / ".env"

load_dotenv(dotenv_path=ENV_PATH)


class Settings(BaseSettings):
    PROJECT_NAME: str
    JWT_ACCESS_TOKEN_EXPIRES_MINUTES: int = 60 * 24
    JWT_REFRESH_TOKEN_EXPIRES_MINUTES: int = 60 * 24 * 100
    JWT_AUDIENCE: str = "pyapp_fastapi"
    JWT_ALGORITHM: str = "RS256"
    JWT_PRIVATE_KEY: Path = BASE_DIR / "certs" / "private.pem"
    JWT_PUBLIC_KEY: Path = BASE_DIR / "certs" / "public.pem"
    DATABASE_USER: str
    DATABASE_PASSWORD: str
    DATABASE_HOST: str
    DATABASE_PORT: int
    DATABASE_NAME: str
    ASYNC_DB_ECHO: bool = True
    ASYNC_DB_URI: str = ""

    @field_validator("ASYNC_DB_URI", mode="after")
    @classmethod
    def db_uri(cls, v: str | None, info: ValidationInfo) -> str | None:
        if isinstance(v, str) and v == "":
            return str(
                PostgresDsn.build(
                    scheme="postgresql+asyncpg",
                    username=info.data["DATABASE_USER"],
                    password=info.data["DATABASE_PASSWORD"],
                    host=info.data["DATABASE_HOST"],
                    port=info.data["DATABASE_PORT"],
                    path=info.data["DATABASE_NAME"],
                )
            )
        return v

    class ConfigDict:
        extra = "ignore"


settings = Settings()
