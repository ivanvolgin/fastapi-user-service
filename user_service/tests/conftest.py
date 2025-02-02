from uuid import UUID, uuid4
import pytest
from typing import Any, Optional, Callable
import pydantic
from pydantic import Field
from httpx import AsyncClient, ASGITransport

from user_service.src.db.base import get_user_manager
from user_service.main import app
from user_service.src.core.interfaces import BaseUserDatabase
from user_service.src.core.security import hash_password
from user_service.src.core.typing import StringType
from user_service.src.db import UserManager


@pydantic.dataclasses.dataclass
class FakeUserTable:
    email: str
    hashed_password: str = hash_password("secret123")
    is_active: bool = True
    is_superuser: bool = False
    is_verified: bool = False
    id: UUID = Field(default_factory=uuid4)


@pytest.fixture(scope="session")
def user():
    return FakeUserTable(email="user@example.com")


@pytest.fixture(scope="session")
def user_verified(request) -> FakeUserTable:
    return FakeUserTable(**{"email": "user_verified@example.com", "is_verified": True})


@pytest.fixture(scope="session")
def user_inactive() -> FakeUserTable:
    return FakeUserTable(**{"email": "user_inactive@example.com", "is_active": False})


@pytest.fixture(scope="session")
def admin() -> FakeUserTable:
    return FakeUserTable(**{"email": "admin@example.com", "is_superuser": True})


@pytest.fixture
def mock_user_db(
    user: FakeUserTable,
    user_verified: FakeUserTable,
    user_inactive: FakeUserTable,
    admin: FakeUserTable,
) -> BaseUserDatabase[FakeUserTable, UUID]:
    class MockUserDatabase(BaseUserDatabase):
        async def get_user_by_email(self, email: StringType) -> Optional[FakeUserTable]:
            if email == user.email:
                return user
            if email == user_verified.email:
                return user_verified
            if email == user_inactive.email:
                return user_inactive
            if email == admin.email:
                return admin

        async def create_user(self, create_dict: dict[str, Any]) -> FakeUserTable:
            return FakeUserTable(**create_dict)

        async def update_user(
            self, update_user: FakeUserTable, updated_dict: dict[str, Any]
        ) -> FakeUserTable:
            for k, v in updated_dict.items():
                setattr(update_user, k, v)
            return update_user

        async def delete_user(self, delete_user: FakeUserTable) -> None:
            pass

        async def get_user_by_id(self, user_id: UUID) -> Optional[FakeUserTable]:
            if user_id == user.id:
                return user
            if user_id == user_verified.id:
                return user_verified
            if user_id == user_inactive.id:
                return user_inactive
            if user_id == admin.id:
                return admin

    return MockUserDatabase()


@pytest.fixture
def user_manager(mock_user_db, mocker):
    user_manager = UserManager(mock_user_db)
    mocker.spy(user_manager, "on_after_register")
    mocker.spy(user_manager, "on_after_login")
    mocker.spy(user_manager, "on_after_update")
    return user_manager


@pytest.fixture
def get_test_user_manager(user_manager):
    def _get_test_user_manager():
        return user_manager

    return _get_test_user_manager


@pytest.fixture
async def client(get_test_user_manager):
    app.dependency_overrides[get_user_manager] = get_test_user_manager
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://localhost:80/"
    ) as client:
        yield client
