import pytest
from fastapi import status
from user_service.src.core.exceptions import ErrorCode
from user_service.tests.conftest import user_manager


@pytest.mark.router
class TestAuth:
    @pytest.mark.parametrize(
        "email",
        [
            "user@example.com",
            "user_verified@example.com",
            "admin@example.com",
        ],
    )
    async def test_login(self, client, email, user_manager):
        response = await client.post(
            "/login", data={"username": email, "password": "secret123"}
        )
        data = response.json()
        assert response.status_code == status.HTTP_200_OK
        assert len(data["access_token"].split(".")) == 3
        assert data["token_type"] == "bearer"
        assert user_manager.on_after_login.called is True

    async def test_login_invalid_email(self, client, user_manager):
        response = await client.post(
            "/login", data={"username": "invalid_email", "password": "secret123"}
        )
        data = response.json()
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert data == {"detail": ErrorCode.LOGIN_BAD_CREDENTIALS}
        assert user_manager.on_after_login.called is False

    @pytest.mark.parametrize(
        "password",
        [
            "",
            "invalid_password",
        ],
    )
    async def test_login_invalid_password(self, client, password, user_manager):
        response = await client.post(
            "/login", data={"username": "user@example.com", "password": password}
        )
        data = response.json()
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert data == {"detail": ErrorCode.LOGIN_BAD_CREDENTIALS}
        assert user_manager.on_after_login.called is False

    async def test_missing_body(self, client, user_manager):
        response = await client.post("/login")
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert user_manager.on_after_login.called is False

    async def test_missing_email(self, client, user_manager):
        response = await client.post("/login", data={"password": "secret123"})
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert user_manager.on_after_login.called is False

    async def test_missing_password(self, client, user_manager):
        response = await client.post("/login", data={"username": "user@example.com"})
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert user_manager.on_after_login.called is False
