from enum import IntEnum

from apps.core.decorators import status_decorator


class UserRole(IntEnum):
    ADMIN = 1
    SELLER = 2


class AuthenticationConsts:
    MINIMUM_PASSWORD_LENGTH = 8


class AuthErrorConsts:
    @status_decorator
    class InvalidEmailFormat:
        code = 1001
        message = 'Invalid email format.'

    @status_decorator
    class PasswordTooShort:
        code = 1002
        message = 'Password must be at least 8 characters long.'

    @status_decorator
    class EmailAlreadyExists:
        code = 1003
        message = 'An account with this email already exists.'

    @status_decorator
    class InvalidCredentials:
        code = 1004
        message = 'Invalid email or password.'

    @status_decorator
    class AccountNotFound:
        code = 1005
        message = 'No account found with this email.'

    @status_decorator
    class EmailRequired:
        code = 1006
        message = 'Email is required.'

    @status_decorator
    class PasswordRequired:
        code = 1007
        message = 'Password is required.'


class LogoutErrorConsts:
    @status_decorator
    class RefreshTokenRequired:
        code = 2001
        message = 'Refresh token is required.'

    @status_decorator
    class InvalidToken:
        code = 2002
        message = 'Invalid or expired refresh token.'
