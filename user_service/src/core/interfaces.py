from typing import Protocol, TypeVar, Optional, Any, Union

from fastapi import Request
from user_service.src.core.typing import StringType
from user_service.src.schemes import UserCreate, UserUpdate

ID = TypeVar("ID", contravariant=True)


class UserProtocol(Protocol):
    """
    Protocol representing the user model.

    This protocol defines the required fields for a user, including the unique identifier,
    email, hashed password, and flags for activity, superuser status, and email verification.
    """

    id: Any
    email: Any
    hashed_password: Any
    is_active: Any
    is_superuser: Any
    is_verified: Any


class UserCreateProtocol(Protocol):
    """
    Protocol for creating a new user.

    This protocol defines the required fields for creating a user, including email, password,
    and flags for activity, superuser status, and email verification.
    """

    email: Any
    password: Any
    is_active: Any
    is_superuser: Any
    is_verified: Any


class UserUpdateProtocol(Protocol):
    """
    Protocol for updating an existing user.

    This protocol defines the fields that can be updated for an existing user, including email, password,
    and flags for activity, superuser status, and email verification. Not all fields are mandatory during
    an update operation.
    """

    email: Any
    password: Any
    is_active: Any
    is_superuser: Any
    is_verified: Any


UP = TypeVar("UP", bound=UserProtocol)
UCP = TypeVar("UCP", bound=UserCreateProtocol)
UUP = TypeVar("UUP", bound=UserUpdateProtocol)


class BaseUserDatabase(Protocol[UP, ID]):
    """
    Protocol for the user database service.

    This protocol defines the methods for interacting with the user database, including getting, creating,
    updating, and deleting users.

    :method get_user_by_id: Fetch a user from the database by their unique identifier.
    :method get_user_by_email: Fetch a user from the database by their email address.
    :method create_user: Create a new user in the database.
    :method update_user: Update an existing user's information in the database.
    :method delete_user: Delete a user from the database.
    """

    async def get_user_by_id(self, user_id: ID) -> Optional[UP]: ...

    async def get_user_by_email(self, email: StringType) -> Optional[UP]: ...

    async def create_user(self, create_dict: dict[str, Any]) -> UP: ...

    async def update_user(self, update_user: UP, update_dict: dict[str, Any]) -> UP: ...

    async def delete_user(self, delete_user: UP) -> None: ...


class BaseUserManager(Protocol[UP, ID]):
    """
    Protocol for managing user-related operations.

    This protocol defines methods for managing users, such as fetching, creating, and updating user data.

    :method get_user_by_email: Fetch a user by their email address.
    :method get_user_by_id: Fetch a user by their unique identifier.
    :method create_user: Create a new user in the system.
    :method update_user: Update an existing user's information.
    """

    async def parse_id(self, user_id: Any) -> ID: ...
    async def get_user_by_email(self, email: StringType) -> Optional[UP]: ...
    async def get_user_by_id(self, user_id: ID) -> Optional[UP]: ...
    async def create_user(
        self, create_dict: UserCreate, request: Optional[Request] = None
    ) -> UP: ...

    async def update_user(
        self,
        update_user: UP,
        update_dict: UserUpdate,
        request: Optional[Request] = None,
    ) -> UP: ...


class BaseTokenService(Protocol[UP, ID]):
    """
    A generic protocol for working with tokens.

    This protocol defines methods for generating and validating tokens in a system,
    allowing it to be used with various types of tokens (e.g., JWT, OAuth, etc.).
    It can be implemented to handle different types of authentication tokens for different users.

    :method read_token: Validates and decodes the provided token, returning the corresponding user if valid.
    :method write_token: Generates a token for the current user.
    """

    async def read_token(
        self, token: Optional[str], user_manager: BaseUserManager[UP, ID]
    ) -> Optional[UP]: ...
    async def write_token(self, current_user: UP) -> str: ...
    async def destroy_token(self, token: str, user: UP) -> None: ...
