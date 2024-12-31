import secrets
import uuid
from typing import Annotated, Any
from fastapi import APIRouter, HTTPException, status, Header, Response
from fastapi.params import Depends, Cookie
from fastapi.security import HTTPBasic, HTTPBasicCredentials

router = APIRouter(prefix="/auth", tags=["Authentication"])

USERS: list[dict[str, str]] = [
    {"username": "admin", "password": "12345"},
    {"username": "Ivan", "password": "11111"},
]

USERS_CREDENTIALS: dict[str, dict[str, str]] = {
    "7be3fc4b8ecb375ded87ca194b1d35ee": {
        "username": "admin",
    },
    "a76e2da19bc16a4955309b36bb867e81": {
        "username": "Ivan",
    },
}
COOKIES: dict[str, dict] = {}
COOKIE_SESSION_TO_KEY = "web-app-session-id"


def generate_session_id() -> str:
    return uuid.uuid4().hex


def verify_password(
    plain_password: str,
    hashed_password: str,
) -> bool:
    return secrets.compare_digest(
        plain_password.encode("utf-8"),
        hashed_password.encode("utf-8"),
    )


def authenticate_user(
    username,
    plain_password,
) -> dict | None:
    for user in USERS:
        if username == user["username"]:
            if hashed_password := user.get("password", None):
                if verify_password(plain_password, hashed_password):
                    return {"username": username}
    return None


async def check_user_credentials(
    credentials: Annotated[HTTPBasicCredentials, Depends(HTTPBasic())]
) -> dict:
    if user := authenticate_user(
        credentials.username,
        credentials.password,
    ):
        return user

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Wrong login or password",
        headers={"WWW-Authenticate": "Basic"},
    )


async def check_user_header(
    static_token: Annotated[str, Header(alias="X-Auth-Token")]
) -> dict:
    if user := USERS_CREDENTIALS.get(static_token, None):
        return user

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid token.",
    )


async def check_login_cookie(
    session_id: Annotated[str, Cookie(alias=COOKIE_SESSION_TO_KEY)]
) -> dict:
    if user := COOKIES.get(session_id, None):
        return user

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid session id.",
    )


@router.get("/basicauth")
async def make_basic_auth(
    user: Annotated[dict, Depends(check_user_credentials)]
) -> dict:
    return {
        "message": "Login successful",
        **user,
    }


@router.get("/header")
async def make_auth_by_header(
    user: Annotated[dict, Depends(check_user_header)]
) -> dict:
    return {
        "message": "Login successful",
        **user,
    }


@router.post("/cookie/login")
async def login_set_cookie(
    response: Response,
    user: Annotated[dict, Depends(check_user_credentials)],
) -> dict:
    session_id = generate_session_id()
    response.set_cookie(COOKIE_SESSION_TO_KEY, session_id)
    COOKIES[session_id] = user
    return {
        "message": "Cookies have been successfully set",
        **user,
    }


@router.get("/cookie")
async def make_auth_by_cookie(
    user: Annotated[dict, Depends(check_login_cookie)]
) -> dict:
    return {
        "message": "Login successful",
        **user,
    }


@router.get("/cookie/delete")
async def make_auth_by_cookie(
    response: Response,
    user: Annotated[dict, Depends(check_login_cookie)],
    session_id: Annotated[str, Cookie(alias=COOKIE_SESSION_TO_KEY)],
) -> dict:
    COOKIES.pop(session_id)
    response.delete_cookie(COOKIE_SESSION_TO_KEY)
    return {
        "message": "Cookies have been successfully deleted",
    }
