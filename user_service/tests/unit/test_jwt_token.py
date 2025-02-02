from typing import Optional, Callable
from uuid import uuid4
import pytest
import pathlib
import asyncio
from user_service.src.core.config import settings
from user_service.src.core.interfaces import ID
from user_service.src.core.jwt_token import (
    JWTTokenService,
    JWTTokenServiceDestroyNotSupportedError,
)
from user_service.src.core.security import decode_jwt, encode_jwt


async def create_private_key(private_key_path: pathlib.Path):
    process = await asyncio.create_subprocess_exec(
        "openssl",
        "genrsa",
        "-out",
        str(private_key_path),
        "2048",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await process.communicate()
    if process.returncode != 0:
        raise RuntimeError(f"OpenSSL returned {process.returncode}: {stderr}")


async def create_public_key(
    private_key_path: pathlib.Path, public_key_path: pathlib.Path
):
    process = await asyncio.create_subprocess_exec(
        "openssl",
        "rsa",
        "-in",
        str(private_key_path),
        "-outform",
        "PEM",
        "-pubout",
        "-out",
        str(public_key_path),
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await process.communicate()
    if process.returncode != 0:
        raise RuntimeError(f"OpenSSL returned {process.returncode}: {stderr}")


@pytest.fixture(scope="module")
def temp_dir(tmp_path_factory) -> pathlib.Path:
    return tmp_path_factory.mktemp("certs")


@pytest.fixture(scope="module")
async def certs(temp_dir):
    private_key_path = temp_dir / "private.pem"
    public_key_path = temp_dir / "public.pem"
    await create_private_key(private_key_path)
    await create_public_key(private_key_path, public_key_path)
    yield {
        "private_key": private_key_path.read_text(),
        "public_key": public_key_path.read_text(),
    }


@pytest.mark.jwt
async def test_create_certs(certs):
    assert certs["private_key"]
    assert certs["public_key"]
    assert "PRIVATE KEY" in certs["private_key"]
    assert "PUBLIC KEY" in certs["public_key"]


@pytest.fixture(scope="module")
def jwt_token_service(certs):
    return JWTTokenService(
        private_key=certs["private_key"],
        public_key=certs["public_key"],
    )


@pytest.fixture()
def jwt_token(certs) -> Callable[[Optional[ID]], str]:
    def _jwt_token(user_id: Optional[ID] = None):
        payload = {
            "aud": settings.JWT_AUDIENCE,
        }
        if user_id:
            payload["sub"] = str(user_id)
        return encode_jwt(
            payload=payload,
            key=certs["private_key"],
            token_expires_delta=settings.JWT_ACCESS_TOKEN_EXPIRES_MINUTES,
            algorithm=settings.JWT_ALGORITHM,
        )

    return _jwt_token


@pytest.mark.jwt
class TestWriteJWTToken:
    async def test_write_jwt_token(self, jwt_token_service, user, certs):
        token = await jwt_token_service.write_token(user)
        assert token
        assert len(token.split(".")) == 3

        decoded_jwt = decode_jwt(token=token, key=certs["public_key"])
        assert decoded_jwt["sub"] == str(user.id)
        assert decoded_jwt["email"] == user.email


@pytest.mark.jwt
class TestReadJWTToken:
    async def test_missing_token(self, jwt_token_service, user_manager):
        user = await jwt_token_service.read_token(None, user_manager)
        assert not user

    async def test_invalid_token(self, jwt_token_service, user_manager):
        user = await jwt_token_service.read_token("invalid", user_manager)
        assert not user

    async def test_invalid_token_missing_user_payload(
        self, jwt_token_service, jwt_token, user_manager
    ):
        user = await jwt_token_service.read_token(jwt_token(), user_manager)
        assert not user

    async def test_invalid_token_invalid_user_id(
        self, jwt_token_service, jwt_token, user_manager
    ):
        user = await jwt_token_service.read_token(jwt_token("invalid"), user_manager)
        assert not user

    async def test_valid_token_not_existing_user(
        self, jwt_token_service, jwt_token, user_manager
    ):
        user = await jwt_token_service.read_token(jwt_token(uuid4()), user_manager)
        assert not user

    async def test_valid_token(self, jwt_token_service, user, user_manager, jwt_token):
        user = await jwt_token_service.read_token(jwt_token(user.id), user_manager)
        assert user


@pytest.mark.jwt
class TestDestroyJWTToken:
    async def test_delete_jwt_token(self, jwt_token_service, user):
        with pytest.raises(
            JWTTokenServiceDestroyNotSupportedError,
            match="Token destroy is not supported for JWT. It`s valid until it expires",
        ):
            await jwt_token_service.destroy_token("TOKEN", user)
