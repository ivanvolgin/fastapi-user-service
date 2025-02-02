from datetime import datetime, UTC
from typing import Optional
from uuid import UUID

from user_service.src.core.exceptions import UserNotExists, InvalidID
from user_service.src.core.security import decode_jwt, encode_jwt
from user_service.src.core.config import settings
from user_service.src.core.interfaces import (
    BaseTokenService,
    UP,
    BaseUserManager,
    ID,
)
from user_service.src.models import UserTable
from jwt import PyJWTError


class JWTTokenServiceDestroyNotSupportedError(Exception):
    def __init__(self, message):
        super().__init__(message)
        self.message = message


class JWTTokenService(BaseTokenService[UP, ID]):
    """
    Service for handling JWT token creation and validation.

    This service is responsible for creating JWT tokens for authenticated users and validating
    incoming JWT tokens. It uses asymmetric keys (public/private key pair) for signing and
    verifying tokens.
    """

    def __init__(
        self,
        /,
        token_expires_delta: int = settings.JWT_ACCESS_TOKEN_EXPIRES_MINUTES,
        token_audience: str = settings.JWT_AUDIENCE,
        algorithm: str = settings.JWT_ALGORITHM,
        public_key: str = settings.JWT_PUBLIC_KEY.read_text(),
        private_key: str = settings.JWT_PRIVATE_KEY.read_text(),
    ):
        """
        Initializes the JWTTokenService with configuration values.

        :param token_expires_delta: The expiration time for the JWT token, in seconds.
        :param token_audience: The intended audience for the JWT token.
        :param algorithm: The algorithm used to sign the JWT token.
        :param public_key: The public key used to verify the JWT token.
        :param private_key: The private key used to sign the JWT token.
        """
        self.token_expires_delta = token_expires_delta
        self.token_audience = token_audience
        self.algorithm = algorithm
        self.public_key = public_key
        self.private_key = private_key

    async def write_token(self, current_user: UP) -> str:
        """
        Generates a JWT token for the specified user.

        This method creates a JWT token containing user information, such as the user's ID and email,
        and signs it using the private key. The token is set to expire based on the configured expiration
        delta.

        :param current_user: The user for whom the JWT token will be created.
        :return: A signed JWT token as a string.
        """
        payload = {
            "sub": str(current_user.id),
            "email": current_user.email,
            "aud": self.token_audience,
            "iat": datetime.now(UTC).timestamp(),
        }
        return encode_jwt(
            payload=payload,
            key=self.private_key,
            token_expires_delta=self.token_expires_delta,
            algorithm=self.algorithm,
        )

    async def read_token(
        self, token: Optional[str], user_manager: BaseUserManager[UserTable, UUID]
    ) -> Optional[UserTable]:
        """
        Decodes and validates the given JWT token.

        This method decodes the JWT token and checks the validity of the token. If the token is valid,
        it retrieves the associated user from the database using the decoded user ID. If any validation
        fails (e.g., token is invalid or user not found), it returns None.

        :param token: The JWT token to be validated and decoded.
        :param user_manager: An instance of the user manager used to fetch user data.
        :return: The corresponding UserTable instance if the token is valid, or None if the token is invalid.
        """
        if not token:
            return None

        try:
            decoded_jwt = decode_jwt(
                token,
                key=self.public_key,
                token_audience=self.token_audience,
                algorithm=self.algorithm,
            )
            user_id = decoded_jwt.get("sub")
            if not user_id:
                return None
        except PyJWTError:
            return None

        try:
            parsed_id = await user_manager.parse_id(user_id)
            return await user_manager.get_user_by_id(parsed_id)
        except (UserNotExists, InvalidID):
            return None

    async def destroy_token(self, token: str, user: UP) -> None:
        raise JWTTokenServiceDestroyNotSupportedError("Token destroy is not supported for JWT. It`s valid until it expires")

async def get_jwt_token_service():
    return JWTTokenService()

