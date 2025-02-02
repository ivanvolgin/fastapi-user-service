from typing import TypeVar, Optional
from uuid import UUID
from pydantic import ConfigDict, EmailStr
from user_service.src.schemes.base import BaseUserModel


class User(BaseUserModel):
    id: UUID
    email: EmailStr
    is_active: bool = True
    is_superuser: bool = False
    is_verified: bool = False

    model_config = ConfigDict(from_attributes=True)


class UserCreate(BaseUserModel):
    email: EmailStr
    password: str
    is_active: Optional[bool] = True
    is_superuser: Optional[bool] = False
    is_verified: Optional[bool] = False


class UserUpdate(BaseUserModel):
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    is_active: Optional[bool] = True
    is_superuser: Optional[bool] = False
    is_verified: Optional[bool] = False


U = TypeVar("U", bound=User)
UC = TypeVar("UC", bound=UserCreate)
UU = TypeVar("UU", bound=UserUpdate)
