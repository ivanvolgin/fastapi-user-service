from typing import Any
from enum import Enum


class FastAPIUsersException(Exception):
    """
    Base exception class for all exceptions related to user operations.
    """

    pass


class InvalidID(FastAPIUsersException):
    """
    Exception raised when an invalid ID is provided.
    """

    pass


class UserAlreadyExists(FastAPIUsersException):
    """
    Exception raised when trying to create a user that already exists.
    """

    pass


class UserNotExists(FastAPIUsersException):
    """
    Exception raised when a user does not exist in the system.
    """

    pass


class UserInactive(FastAPIUsersException):
    """
    Exception raised when an inactive user is being accessed or operated upon.
    """

    pass


class UserAlreadyVerified(FastAPIUsersException):
    """
    Exception raised when trying to verify a user who is already verified.
    """

    pass


class InvalidVerifyToken(FastAPIUsersException):
    """
    Exception raised when an invalid verification token is provided.
    """

    pass


class InvalidResetPasswordToken(FastAPIUsersException):
    """
    Exception raised when an invalid password reset token is provided.
    """

    pass


class InvalidPasswordException(FastAPIUsersException):
    """
    Exception raised when a password is invalid.

    :param reason: The reason for the invalid password exception (e.g., too weak, incorrect format).
    """
    def __init__(self, message) -> None:
        super().__init__(message)
        self.message = message


class ErrorCode(str, Enum):
    """
    Enum representing various error codes for user-related operations.

    Each error code corresponds to a specific error scenario that may occur during user authentication,
    registration, verification, and password management.
    """

    REGISTER_INVALID_PASSWORD = "REGISTER_INVALID_PASSWORD"
    REGISTER_USER_ALREADY_EXISTS = "REGISTER_USER_ALREADY_EXISTS"
    OAUTH_NOT_AVAILABLE_EMAIL = "OAUTH_NOT_AVAILABLE_EMAIL"
    OAUTH_USER_ALREADY_EXISTS = "OAUTH_USER_ALREADY_EXISTS"
    LOGIN_BAD_CREDENTIALS = "LOGIN_BAD_CREDENTIALS"
    LOGIN_USER_NOT_VERIFIED = "LOGIN_USER_NOT_VERIFIED"
    RESET_PASSWORD_BAD_TOKEN = "RESET_PASSWORD_BAD_TOKEN"
    RESET_PASSWORD_INVALID_PASSWORD = "RESET_PASSWORD_INVALID_PASSWORD"
    VERIFY_USER_BAD_TOKEN = "VERIFY_USER_BAD_TOKEN"
    VERIFY_USER_ALREADY_VERIFIED = "VERIFY_USER_ALREADY_VERIFIED"
    UPDATE_USER_EMAIL_ALREADY_EXISTS = "UPDATE_USER_EMAIL_ALREADY_EXISTS"
    UPDATE_USER_INVALID_PASSWORD = "UPDATE_USER_INVALID_PASSWORD"



