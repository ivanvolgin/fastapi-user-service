from user_service.main import app
from user_service.src.core.exceptions import ErrorCode
from user_service.src.db.base import get_user_manager
import pytest
from httpx import AsyncClient, ASGITransport
from fastapi import status


@pytest.mark.router
class TestRegister:
    async def test_empty_body(self, client: AsyncClient):
        response = await client.post("/register", json={})
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_missing_email(self, client: AsyncClient):
        response = await client.post("/register", json={"password": "secret123"})
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_missing_password(self, client: AsyncClient):
        response = await client.post(
            "/register", json={"email": "register@example.com"}
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_register_invalid_email(self, client):
        response = await client.post(
            "/register",
            json={"email": "invalid_email", "password": "secret123"},
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.parametrize(
        "password, expected_message",
        [
            ("", "Password must be at least 8 characters long."),
            ("qwerty", "Password must be at least 8 characters long."),
            ("password", "Password must contain at least 1 number."),
            ("123456789", "Password must contain at least 1 letter."),
        ],
    )
    async def test_register_invalid_password(self, client, password, expected_message):
        response = await client.post(
            "/register",
            json={"email": "user@example.com", "password": password},
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == {
            "detail": {
                "error_code": ErrorCode.REGISTER_INVALID_PASSWORD,
                "message": expected_message,
            }
        }

    async def test_register(self, client):
        response = await client.post(
            "/register",
            json={"email": "register_user@example.com", "password": "secret123"},
        )
        assert response.status_code == status.HTTP_201_CREATED

    async def test_register_already_registered(self, client):
        response = await client.post(
            "/register",
            json={"email": "user@example.com", "password": "secret123"},
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == {
            "detail": ErrorCode.REGISTER_USER_ALREADY_EXISTS,
        }
