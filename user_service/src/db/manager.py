from typing import Optional, Any
from uuid import UUID
from fastapi import Request
from fastapi.security import OAuth2PasswordRequestForm
from user_service.src.core.interfaces import UP, ID, BaseUserManager, BaseUserDatabase
from user_service.src.core.typing import StringType
from user_service.src.db.database import SQLAlchemyUserDatabase
from user_service.src.models import UserTable
from user_service.src.core.exceptions import (
    UserAlreadyExists,
    UserNotExists,
    InvalidID,
    InvalidPasswordException,
    ErrorCode,
)
from user_service.src.core.security import (
    hash_password,
    verify_password,
    validate_password,
    verify_and_update_password,
)
from user_service.src.schemes import UserCreate, UserUpdate, model_dump


class UserManager(BaseUserManager[UserTable, UUID]):
    """
    Manager class for handling user-related operations like creation, update, and authentication.
    This class interacts with the user database and handles logic for user management.

    :param user_db: Database interface for user-related operations.
    """

    user_db: BaseUserDatabase[UserTable, UUID]

    def __init__(self, user_db: BaseUserDatabase[UserTable, UUID]):
        self.user_db: BaseUserDatabase[UserTable, UUID] = user_db

    async def parse_id(self, user_id: Any) -> UUID:
        try:
            parsed_id = UUID(user_id)
        except Exception:
            raise InvalidID()
        return parsed_id

    async def create_user(
        self, user_create: UserCreate, request: Optional[Request] = None
    ) -> UserTable:
        """
        Create a new user in the database.

        :param user_create: Data required to create a new user.
        :param request: Optional FastAPI Request object, useful for logging or additional context.
        :raises UserAlreadyExists: Raised if a user with the provided data already exists in the database.
        :return: The newly created user.
        """

        validate_password(user_create.password)
        existing_user = await self.user_db.get_user_by_email(user_create.email)
        if existing_user:
            raise UserAlreadyExists()
        user_dict = user_create.create_update_dict()
        password = user_dict.pop("password")
        user_dict["hashed_password"] = hash_password(password)
        created_user = await self.user_db.create_user(user_dict)
        await self.on_after_register(created_user, request)
        return created_user

    async def get_user_by_email(self, email: StringType) -> Optional[UserTable]:
        """
        Get a user by email.

        :param email: The email address of the user.
        :raise UserNotExists: Raised if a user with the specified email does not exist in the database.
        :return: The existing user with the specified email retrieved from the database.
        """

        user = await self.user_db.get_user_by_email(email)
        if not user:
            raise UserNotExists()
        return user

    async def get_user_by_id(self, user_id: UUID) -> Optional[UserTable]:
        """
        Get a user by ID.

        :param user_id: The unique identifier of the user (UUID).
        :raises UserNotExists: Raised if a user with the specified ID does not exist in the database.
        :return: The existing user with the specified ID retrieved from the database.
        """
        user = await self.user_db.get_user_by_id(user_id)
        if not user:
            raise UserNotExists()
        return user

    async def update_user(
        self,
        user: UserTable,
        update_dict: UserUpdate,
        request: Optional[Request] = None,
    ) -> UserTable:
        """
        Update user data in the database.

        :param user: The SQLAlchemy ORM model instance representing the user to update.
        :param update_dict: An object containing the updated user data.
        :param request: Optional FastAPI Request object, useful for logging or additional context.
        :return: The updated UserTable instance reflecting the changes.
        """
        update_data = update_dict.create_update_dict()
        updated_user = await self._update_user(user, update_data)
        await self.on_after_update(request)
        return updated_user

    async def authenticate(
        self, credentials: OAuth2PasswordRequestForm
    ) -> Optional[UserTable]:
        """
        Authenticate a user based on provided credentials.

        This method checks the user's credentials and verifies the password.
        If the password is incorrect, it returns None. If the user is found and
        the password is valid, the user object is returned, potentially with
        an updated password hash.

        :param credentials: OAuth2PasswordRequestForm containing the user's username (email) and password.
        :return: The authenticated UserTable instance if the credentials are valid, or None if authentication fails.
        """
        try:
            user = await self.get_user_by_email(credentials.username)
        except UserNotExists:
            hash_password(credentials.password)
            return None

        if user:
            verified, updated_password_hash = verify_and_update_password(
                credentials.password,
                str(user.hashed_password),
            )
            if not verified:
                return None

            if updated_password_hash:
                user = await self.user_db.update_user(
                    user,
                    {"hashed_password": updated_password_hash},
                )
            return user
        return None

    async def _update_user(
        self, user: UserTable, update_dict: dict[str, Any]
    ) -> UserTable:
        validate_dict = {}
        for k, v in update_dict.items():
            if k == "email" and v != user.email:
                try:
                    await self.get_user_by_email(v)
                    raise UserAlreadyExists(ErrorCode.UPDATE_USER_EMAIL_ALREADY_EXISTS)
                except UserNotExists:
                    validate_dict["email"] = v
                    validate_dict["is_verified"] = False
            elif k == "password":
                if not verify_password(v, user.hashed_password):
                    password = update_dict["password"]
                    validate_password(password)
                    validate_dict["hashed_password"] = hash_password(password)
                else:
                    raise InvalidPasswordException(
                        ErrorCode.UPDATE_USER_INVALID_PASSWORD
                    )
            else:
                validate_dict[k] = v
        return await self.user_db.update_user(user, validate_dict)

    async def on_after_register(
        self,
        created_user: UserTable,
        request: Optional[Request] = None,
    ):
        """
        Hook method called after a new user is registered.

        This method can be used for post-registration tasks, such as sending a welcome email
        or logging the registration event.

        :param created_user: The UserTable instance representing the newly created user.
        :param request: Optional FastAPI Request object, which may provide context for the registration event.
        """
        pass

    async def on_after_update(self, request: Optional[Request] = None):
        """
        Hook method called after a user is updated.

        This method can be used for post-update tasks, such as logging the update event
        or notifying the user of changes to their account.

        :param request: Optional FastAPI Request object, which may provide context for the update event.
        """
        pass

    async def on_after_login(
        self, user, request: Optional[Request] = None, response=None
    ):
        pass
