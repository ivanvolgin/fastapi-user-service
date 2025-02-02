from typing import Annotated
from fastapi import APIRouter, Request, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from user_service.src.core.exceptions import ErrorCode
from user_service.src.db.base import get_user_manager
from user_service.src.db import UserManager
from user_service.src.schemes.bearer import BearerResponse
from user_service.src.core.jwt_token import get_jwt_token_service, JWTTokenService

router = APIRouter()


@router.post(
    "/login",
    response_model=BearerResponse,
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_400_BAD_REQUEST: {
            "model": ErrorCode,
            "content": {
                "application/json": {
                    "examples": {
                        ErrorCode.LOGIN_BAD_CREDENTIALS: {
                            "summary": "Invalid credentials or user is not active.",
                            "value": {"detail": ErrorCode.LOGIN_BAD_CREDENTIALS},
                        }
                    },
                }
            },
        },
    },
)
async def login(
    request: Request,
    credentials: Annotated[OAuth2PasswordRequestForm, Depends()],
    user_manager: Annotated[UserManager, Depends(get_user_manager)],
    jwt_token_service: Annotated[JWTTokenService, Depends(get_jwt_token_service)],
):
    user = await user_manager.authenticate(credentials)
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorCode.LOGIN_BAD_CREDENTIALS,
        )
    access_token = await jwt_token_service.write_token(user)
    response = BearerResponse(access_token=access_token, token_type="bearer")
    await user_manager.on_after_login(user, request, response)
    return response
