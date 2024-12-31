from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str

    class Config:
        env_file = "/home/ramb1zzy/pyapp/.env"


settings = Settings()

if __name__ == "__main__":
    print(settings.database_url)
