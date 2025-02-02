from unittest.mock import AsyncMock
import pytest
from pydantic_core._pydantic_core import ValidationError

from user_service.src.core.exceptions import (
    ErrorCode,
    InvalidPasswordException,
    UserAlreadyExists,
    UserNotExists,
)
from user_service.src.core.typing import StringType
from user_service.src.db import UserManager
from user_service.src.schemes import UserCreate, UserUpdate
from user_service.tests.conftest import FakeUserTable


@pytest.mark.manager
class TestCreateUser:
    @pytest.mark.parametrize(
        "email",
        [
            "User@example.com",
            "user_verified@example.com",
            "user_INActive@example.com",
            "ADMIN@EXAMPLE.COM",
        ],
    )
    async def test_create_existing_user(
        self,
        user_manager: AsyncMock,
        email: StringType,
    ):
        user = UserCreate(email=email, password="secret123")
        with pytest.raises(UserAlreadyExists):
            await user_manager.create_user(user)
        assert user_manager.on_after_register.called is False

    async def test_create_user_invalid_email(self):
        with pytest.raises(ValidationError):
            user = UserCreate(email="invalid_email", password="secret123")

    @pytest.mark.parametrize(
        "password, expected_message",
        [
            ("", "Password must be at least 8 characters long."),
            ("qwerty", "Password must be at least 8 characters long."),
            ("password", "Password must contain at least 1 number."),
            ("123456789", "Password must contain at least 1 letter."),
        ],
    )
    async def test_create_user_invalid_password(
        self, user_manager: AsyncMock, password: str, expected_message: str
    ):
        user = UserCreate(email="invalid_password@example.com", password=password)
        with pytest.raises(InvalidPasswordException, match=expected_message):
            await user_manager.create_user(user)
        assert user_manager.on_after_register.called is False

    @pytest.mark.parametrize(
        "email", ["user_create@example.com", "user_CREATE@example.com"]
    )
    async def test_create_valid_user(self, user_manager: AsyncMock, email: StringType):
        user = UserCreate(email=email, password="secret123")
        created_user = await user_manager.create_user(user)
        assert len(created_user.__annotations__) == 6
        assert created_user.email == email.lower()
        assert created_user.hashed_password.startswith("$2b$")
        assert user_manager.on_after_register.called is True


@pytest.mark.manager
class TestUserManager:
    async def test_update_user_invalid_password(
        self, user_manager: UserManager, user: FakeUserTable
    ):
        update_dict = UserUpdate(**{"password": "secret123"})
        with pytest.raises(
            InvalidPasswordException, match=ErrorCode.UPDATE_USER_INVALID_PASSWORD
        ):
            await user_manager.update_user(user, update_dict)
