from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncConnection,
)
from app.core.config import settings
from app.db.models.base import Base

engine = create_async_engine(
    url=settings.ASYNC_DATABASE_URI,
    echo=settings.DATABASE_ECHO,
)

async_session = async_sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)


async def init_db() -> None:
    print("Инициализация базы данных...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("База данных инициализирована.")


async def get_connection() -> AsyncConnection:
    async with engine.connect() as conn:
        yield conn
