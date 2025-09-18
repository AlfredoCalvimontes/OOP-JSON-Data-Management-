from typing import Any


class AppError(Exception):
    """Base class for custom exceptions in this application."""

    def __init__(self, message: str):
        self.message = message
        super().__init__(message)

    def __str__(self):
        return f"{type(self).__name__}: {self.message}"


class AuthenticationError(AppError):
    """Raised for authentication-related failures."""

    pass


class SessionError(AuthenticationError):
    """Raised for session-related failures."""

    pass


class PasswordAuthenticationError(AuthenticationError):
    """Raised for password authentication-related failures."""

    pass


class InputError(AppError):
    """Raised for interface input failures."""

    pass


class ValidationError(AppError):
    """Raised for data validation failures."""

    def __init__(self, message: str, value: Any, param_name: str):
        self.message = message
        self.value = value
        self.param_name = param_name
        super().__init__(message)

    def __str__(self):
        type_name = type(self).__name__
        return f"{type_name}: Param: {self.param_name} with value: \
            {self.value}. {self.message}"


class DataError(AppError):
    """Raised for data-related failures."""

    pass


class TaskError(DataError):
    """Raised for task-related failures."""

    pass


class TaskNotFoundError(TaskError):
    """Raised when a specific task is not found."""

    pass


class UserError(DataError):
    """Raised for user-related failures."""

    pass


class UserNotFoundError(UserError):
    """Raised when a specific user is not found."""

    pass


class TaskSetError(DataError):
    """Raised for task set-related failures."""

    pass


class UserSetError(DataError):
    """Raised for user set-related failures."""

    pass


class FileError(AppError):
    """Raised for file management-related failures."""

    pass
