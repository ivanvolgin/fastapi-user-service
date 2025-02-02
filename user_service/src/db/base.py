from typing import AsyncGenerator, Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from user_service.src.core.config import settings
from user_service.src.db.database import SQLAlchemyUserDatabase
from user_service.src.db.manager import UserManager
from user_service.src.models import UserTable, Base

engine = create_async_engine(
    url=settings.ASYNC_DB_URI,
    echo=settings.ASYNC_DB_ECHO,
)

async_session_maker = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_db(
    async_session: Annotated[AsyncSession, Depends(get_async_session)]
) -> AsyncGenerator[SQLAlchemyUserDatabase, None]:
    yield SQLAlchemyUserDatabase(
        async_session,
        UserTable,
    )


async def get_user_manager(
    user_db: Annotated[SQLAlchemyUserDatabase, Depends(get_db)]
) -> AsyncGenerator[UserManager, None]:
    yield UserManager(user_db)
