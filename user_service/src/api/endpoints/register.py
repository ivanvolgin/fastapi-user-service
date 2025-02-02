from fastapi import (
    APIRouter,
    status,
    Depends,
    HTTPException,
)
from typing import Annotated
from user_service.src.core.exceptions import (
    InvalidPasswordException,
    UserAlreadyExists,
    ErrorCode,
)
from user_service.src.db.base import get_user_manager
from user_service.src.db import UserManager
from user_service.src.schemes import model_validate, User, ErrorModel, UserCreate

router = APIRouter()


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    response_model=User,
    name="register",
    responses={
        status.HTTP_400_BAD_REQUEST: {
            "model": ErrorModel,
            "content": {
                "application/json": {
                    "examples": {
                        ErrorCode.REGISTER_USER_ALREADY_EXISTS: {
                            "summary": "A user with this email already exists.",
                            "value": {"detail": ErrorCode.REGISTER_USER_ALREADY_EXISTS},
                        },
                        ErrorCode.REGISTER_INVALID_PASSWORD: {
                            "summary": "The password is incorrect.",
                            "value": {"detail": ErrorCode.REGISTER_INVALID_PASSWORD},
                        },
                    }
                }
            },
        }
    },
)
async def register(
    user_create: UserCreate,
    user_manager: Annotated[UserManager, Depends(get_user_manager)],
):
    try:
        created_user = await user_manager.create_user(user_create)
    except InvalidPasswordException as err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error_code": ErrorCode.REGISTER_INVALID_PASSWORD,
                "message": err.message,
            },
        )
    except UserAlreadyExists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorCode.REGISTER_USER_ALREADY_EXISTS,
        )
    return model_validate(User, created_user)
