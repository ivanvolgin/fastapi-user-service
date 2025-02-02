from typing import Optional

from sqlalchemy import Integer, String, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from .base import BaseUserTable, BaseOAuthAccountTable


# fmt: off
class UserTable(BaseUserTable):

    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(1024), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
# fmt: on


class OAuthAccountTable(BaseOAuthAccountTable):
    __tablename__ = "oauth_accounts"

    oauth_name: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    access_token: Mapped[str] = mapped_column(String(1024), nullable=False)
    expires_at: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    refresh_token: Mapped[Optional[str]] = mapped_column(String(1024), nullable=True)
    account_id: Mapped[str] = mapped_column(String(320), index=True, nullable=False)
    account_email: Mapped[str] = mapped_column(String(100), nullable=False)
