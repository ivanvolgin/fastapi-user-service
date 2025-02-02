import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.exc import IntegrityError
from typing import AsyncGenerator
from user_service.src.models import Base, UserTable, OAuthAccountTable
from user_service.src.db import SQLAlchemyUserDatabase


@pytest_asyncio.fixture(scope="function")
async def user_db() -> AsyncGenerator[SQLAlchemyUserDatabase, None]:
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async_session_maker = async_sessionmaker(
        engine,
        expire_on_commit=False,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session_maker() as session:
        yield SQLAlchemyUserDatabase(session, UserTable)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


async def test_queries(user_db: SQLAlchemyUserDatabase):
    user_create_dict = {
        "email": "create@example.com",
        "hashed_password": "$2b$password123456789",
    }

    # Create
    user = await user_db.create_user(user_create_dict)
    assert user is not None
    assert user.email == user_create_dict["email"]
    assert user.hashed_password.startswith("$2b$")
    assert user.is_active is True
    assert user.is_superuser is False

    # Get_User_By_Id
    id_user = await user_db.get_user_by_id(user.id)
    assert id_user.id is not None
    assert id_user.id == user.id

    # Get_User_By_Email
    email_user = await user_db.get_user_by_email(user_create_dict["email"])
    assert email_user.email is not None
    assert email_user.email == user_create_dict["email"]

    # Update
    user_update_dict = {
        "email": "update@example.com",
        "is_verified": True,
    }
    updated_user = await user_db.update_user(
        user,
        user_update_dict,
    )
    assert updated_user.id is not None
    assert updated_user.id == user.id
    assert updated_user.email == user_update_dict["email"]
    assert updated_user.is_verified is user_update_dict["is_verified"]

    # Delete
    await user_db.delete_user(updated_user)
    deleted_user = await user_db.get_user_by_id(user.id)
    assert deleted_user is None


async def test_create_existing_user(user_db: SQLAlchemyUserDatabase):
    user_create_dict = {
        "email": "create@example.com",
        "hashed_password": "$2b$password123456789",
    }
    user = await user_db.create_user(user_create_dict)

    with pytest.raises(IntegrityError):
        await user_db.create_user(user_create_dict)
