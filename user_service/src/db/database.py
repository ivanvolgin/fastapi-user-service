from typing import Optional, Union, AnyStr, Any
from uuid import UUID
from sqlalchemy import select, Select
from sqlalchemy.ext.asyncio import AsyncSession

from user_service.src.core.interfaces import BaseUserDatabase
from user_service.src.core.typing import StringType
from user_service.src.models import UserTable, OAuthAccountTable


class SQLAlchemyUserDatabase(BaseUserDatabase[UserTable, UUID]):
    """
    SQLAlchemy implementation of the user database interface.

    This class interacts with a SQLAlchemy database to perform CRUD operations
    for users and their associated OAuth accounts.

    :param session: SQLAlchemy AsyncSession instance for interacting with the database.
    :param user_table: The SQLAlchemy model representing the user table.
    :param oauth_account_table: Optional SQLAlchemy model representing the OAuth account table.
    """

    session: AsyncSession
    user_table: type[UserTable]
    oauth_account_table: Optional[type[OAuthAccountTable]]

    def __init__(
        self,
        session: AsyncSession,
        user_table: type[UserTable],
        oauth_account_table: Optional[type[OAuthAccountTable]] = None,
    ):
        self.session = session
        self.user_table = user_table
        self.oauth_account_table = oauth_account_table

    async def get_user_by_id(self, user_id: UUID) -> Optional[UserTable]:
        """
        Retrieves a user by their unique ID.

        :param user_id: The ID of the user.
        :return: The user object if found, otherwise None.
        """
        statement = select(self.user_table).where(self.user_table.id == user_id)
        return await self._get_user(statement)

    async def get_user_by_email(self, email: StringType) -> Optional[UserTable]:
        """
        Retrieves a user by their email.

        :param email: The email of the user.
        :return: The user object if found, otherwise None.
        """
        statement = select(self.user_table).where(self.user_table.email == email)
        return await self._get_user(statement)

    async def get_by_oauth_account(
        self, oauth: str, account_id: str
    ) -> Optional[UserTable]:
        """
        Retrieves a user by their OAuth account details.

        :param oauth: The OAuth provider name.
        :param account_id: The OAuth account ID.
        :return: The user object if found, otherwise None.
        :raises NotImplementedError: If OAuth support is not available.
        """
        if not self.oauth_account_table:
            raise NotImplementedError()

        statement = (
            select(self.user_table)
            .join(self.oauth_account_table)
            .where(self.oauth_account_table.oauth_name == oauth)
            .where(self.oauth_account_table.account_id == account_id)
        )

        return await self._get_user(statement)

    async def create_user(self, create_dict: dict[str, Any]) -> UserTable:
        """
        Creates a new user in the database.

        :param create_dict: Dictionary of user attributes to create the new user.
        :return: The created user object.
        """
        user = self.user_table(**create_dict)
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def update_user(
        self,
        user: UserTable,
        update_dict: dict[str, Union[str, bool]],
    ) -> UserTable:
        """
        Updates an existing user in the database.

        :param user: The user object to be updated.
        :param update_dict: Dictionary of attributes to update for the user.
        :return: The updated user object.
        """
        for k, v in update_dict.items():
            setattr(user, k, v)
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def delete_user(self, user: UserTable) -> None:
        """
        Deletes a user from the database.

        :param user: The user object to delete.
        """
        await self.session.delete(user)
        await self.session.commit()

    async def update_oauth_account(
        self,
        user: UserTable,
        oauth_account: OAuthAccountTable,
        update_dict: dict[str, Union[str, bool]],
    ) -> UserTable:
        """
        Updates an OAuth account associated with a user.

        :param user: The user associated with the OAuth account.
        :param oauth_account: The OAuth account to update.
        :param update_dict: Dictionary of attributes to update for the OAuth account.
        :return: The user object.
        :raises NotImplementedError: If OAuth support is not available.
        """
        if not self.oauth_account_table:
            raise NotImplementedError()

        for key, value in update_dict.items():
            setattr(oauth_account, key, value)
        self.session.add(oauth_account)
        await self.session.commit()

        return user

    async def _get_user(self, statement: Select) -> Optional[UserTable]:
        result = await self.session.execute(statement)
        return result.unique().scalar_one_or_none()
