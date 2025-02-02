from datetime import timedelta, datetime, UTC
from typing import Union, Any, Optional
from passlib.context import CryptContext
import jwt
from user_service.src.core.config import settings
from user_service.src.core.exceptions import InvalidPasswordException
from user_service.src.core.typing import StringType

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return password_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_context.verify(plain_password, hashed_password)


def validate_password(password: str):
    if len(password) < 8:
        raise InvalidPasswordException("Password must be at least 8 characters long.")
    elif not any(ch.isdigit() for ch in password):
        raise InvalidPasswordException("Password must contain at least 1 number.")
    elif not any(ch.isalpha() for ch in password):
        raise InvalidPasswordException("Password must contain at least 1 letter.")
    return


def verify_and_update_password(
    plain_password: str, hashed_password: str
) -> tuple[bool, Union[str, None]]:
    return password_context.verify_and_update(plain_password, hashed_password)


def encode_jwt(
    payload: dict[str, Any],
    key: str = settings.JWT_PRIVATE_KEY.read_text(),
    token_expires_delta: Optional[int] = settings.JWT_ACCESS_TOKEN_EXPIRES_MINUTES,
    algorithm: str = settings.JWT_ALGORITHM,
    header: Optional[dict[str, str]] = None,
):
    payload = payload.copy()
    if token_expires_delta:
        payload["exp"] = datetime.now(UTC) + timedelta(minutes=token_expires_delta)
    jwt_encoded = jwt.encode(
        payload=payload,
        key=key,
        algorithm=algorithm,
        headers=header,
    )
    return jwt_encoded


def decode_jwt(
    token: str | bytes,
    key: str = settings.JWT_PUBLIC_KEY.read_text(),
    token_audience: str = settings.JWT_AUDIENCE,
    algorithm: str = settings.JWT_ALGORITHM,
):
    jwt_decoded = jwt.decode(
        jwt=token,
        key=key,
        audience=token_audience,
        algorithms=[algorithm],
    )
    return jwt_decoded
