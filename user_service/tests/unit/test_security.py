import uuid
import pytest
from jwt.exceptions import InvalidKeyError
from user_service.src.core.security import (
    hash_password,
    verify_password,
    verify_and_update_password,
    encode_jwt,
    decode_jwt,
    validate_password,
)
from user_service.src.core.exceptions import InvalidPasswordException


@pytest.fixture
def password() -> str:
    return "123456789qwerty!@#"


@pytest.mark.password
async def test_hash_password(password: str) -> None:
    hashed_password = hash_password(password)

    assert hashed_password != password
    assert hashed_password.startswith("$2b$")
    assert verify_password(password, hashed_password)


@pytest.mark.password
async def test_verify_password(password: str) -> None:
    hashed_password = hash_password(password)

    assert verify_password(password, hashed_password)


@pytest.mark.password
async def test_verify_password_failure(password: str) -> None:
    hashed_password = hash_password(password)

    assert not verify_password("invalid_password", hashed_password)


@pytest.mark.password
async def test_verify_and_update_password(password: str) -> None:
    hashed_password = hash_password(password)
    verified, updated_password_hash = verify_and_update_password(
        password,
        hashed_password,
    )

    assert verified
    assert updated_password_hash != password
    assert updated_password_hash != hashed_password
    if updated_password_hash:
        assert updated_password_hash.startswith("$2b$")


@pytest.mark.password
@pytest.mark.parametrize(
    "plain_password, expected_message",
    [
        ("qw32", "Password must be at least 8 characters long."),
        ("qwertyqwrq", "Password must contain at least 1 number."),
        ("12412123", "Password must contain at least 1 letter."),
        ("correct_password123", None),
    ],
)
async def test_validate_password(plain_password, expected_message) -> None:
    if expected_message:
        with pytest.raises(InvalidPasswordException, match=expected_message):
            validate_password(plain_password)
    else:
        validate_password(plain_password)


@pytest.mark.jwt
class TestEncodeJWT:
    async def test_encode_jwt_invalid_sub_type(self) -> None:
        user_id_in_uuid = uuid.uuid4()
        data = {
            "sub": user_id_in_uuid,
        }

        with pytest.raises(TypeError):
            encode_jwt(data)

    async def test_encode_jwt_invalid_private_key(self) -> None:
        data = {
            "sub": "example",
        }

        with pytest.raises(InvalidKeyError):
            encode_jwt(data, key="invalid_key")

    async def test_encode_jwt(self) -> None:
        user_id_in_uuid = str(uuid.uuid4())
        data = {
            "iss": "pyapp.local",
            "sub": user_id_in_uuid,
            "aud": "pyapp_fastapi",
        }
        jwt_encoded = encode_jwt(data)
        assert len(jwt_encoded.split(".")) == 3

        decoded_jwt = decode_jwt(jwt_encoded)
        assert decoded_jwt["sub"] == user_id_in_uuid
        assert decoded_jwt["iss"] == "pyapp.local"
