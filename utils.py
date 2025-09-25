import argparse
import uuid
from typing import Any

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

import data_management
from constants import (
    TASK_STATUSES,
    USERNAME_LENGTH,
    PASSWORD_LENGTH,
    TASK_TITLE_LENGTH,
    TASK_DESCRIPTION_LENGTH,
)
from error_management.exception_utils import validation_exception_manager
from error_management.exceptions import (
    PasswordAuthenticationError,
    TaskNotFoundError,
    ValidationError,
)
from logging_utils import get_logger


state = data_management.get_persistent_data()
hasher = PasswordHasher()
logger = get_logger(__name__)


# ////// Inner validation funcrtions \\\\\\ #


@validation_exception_manager
def is_valid_text(value: str, param_name: str, is_one_word: bool) -> bool:
    """
    Returns True if value is a string and it's a propper text,
    excluding spaces if is_one_word is True.
    """
    if not isinstance(value, str):
        raise ValidationError("It should be a string.", value, param_name)
    if is_one_word:
        if not value.isalnum():
            raise ValidationError(
                "It should contain only letters and numbers.",
                value,
                param_name,
            )
    else:
        if not all(char.isalnum() or char.isspace() for char in value):
            raise ValidationError(
                "It should contain only letters and numbers.",
                value,
                param_name,
            )
    return True


@validation_exception_manager
def is_longer_than(value: str, param_name: str, long: int) -> bool:
    """Returns True if the text lenght is longer than the requested long."""
    if len(value) >= long:
        return True
    else:
        raise ValidationError(
            f"It should be at least {long} characters long.", value, param_name
        )


@validation_exception_manager
def is_less_than(value: str, param_name: str, long: int) -> bool:
    """
    Returns True if the text lenght is less or equal than the requested long.
    """
    if len(value) <= long:
        return True
    else:
        raise ValidationError(
            f"It should be {long} characters long maximum.", value, param_name
        )


@validation_exception_manager
def is_valid_word(value: str, param_name: str, long: int) -> bool:
    """Returns True if the value is propper word and it's lenght is longer
    than the requested long."""
    if not is_valid_text(value, param_name, True):
        return False
    if not is_longer_than(value, param_name, long):
        return False
    return True


@validation_exception_manager
def is_valid_sentence(value: str, param_name: str, long: int) -> bool:
    """
    Returns True if the value is propper text with spaces and it's
    lenght is less than the requested long.
    """
    if not is_valid_text(value, param_name, False):
        return False
    if not is_less_than(value, param_name, long):
        return False
    return True


@validation_exception_manager
def validate_user_not_exists(username: str) -> bool:
    """
    Returns True if the username doesn't exist and it isn't registered.
    """
    user_exists = (
        state["userset"].user_exists(username)
        if state["userset"] is not None
        else False
    )
    if user_exists:
        raise ValidationError(
            f"Username {username} already exists. Use another one.",
            username,
            "username",
        )
    else:
        return True


def verify_task_uuid_exists(uuid_text: str) -> bool:
    """
    Returns True if the Task UUID is used in an actual Task object in the \
    Task Set.
    """
    try:
        task = (
            state["taskset"].get_task_by_uuid(uuid_text)
            if state["taskset"] is not None
            else None
        )
        if task is None:
            raise TaskNotFoundError(
                f"The Task UUID {uuid_text} is not used in a Task"
            )
        else:
            return True
    except TaskNotFoundError as tnfe:
        logger.warning(f"verify_task_uuid_exists: TaskNotFoundError: {tnfe}")
        return False
    except Exception as e:
        logger.error(f"verify_task_uuid_exists: Error: {e}")
        return False


@validation_exception_manager
def verify_uuid(uuid_text: str) -> bool:
    """Returns True if the uuid in text is valid."""
    try:
        uuid.UUID(uuid_text, version=4)
        return True
    except ValueError:
        raise ValidationError(
            "The Task UUID is not valid.", uuid_text, "uuid_text"
        )


# ////// One Parameter Validation functions for askData \\\\\\ #


@validation_exception_manager
def is_valid_title(title: str) -> bool:
    """
    Returns True if the title is a proper sentences validating the lenght.
    """
    return is_valid_sentence(title, "Title", TASK_TITLE_LENGTH)


@validation_exception_manager
def is_valid_description(description: str) -> bool:
    """
    Returns True if the description is a proper sentences validating the \
    lenght.
    """
    return is_valid_sentence(
        description, "Description", TASK_DESCRIPTION_LENGTH
    )


@validation_exception_manager
def is_valid_name(name: str) -> bool:
    """Returns True if the name is a propper word."""
    return is_valid_word(name, "Name", USERNAME_LENGTH)


@validation_exception_manager
def is_valid_not_existing_name(name: str) -> bool:
    """
    Returns True if the name is a propper word and
    it doesn't exist.
    """
    if not validate_user_not_exists(name):
        return False
    return is_valid_word(name, "Name", USERNAME_LENGTH)


@validation_exception_manager
def is_valid_pass(password: str) -> bool:
    """Returns True if the password is a propper word."""
    return is_valid_word(password, "Password", PASSWORD_LENGTH)


@validation_exception_manager
def verify_task_uuid(uuid_text: str) -> bool:
    """Returns True if the uuid in text is valid and if it's used in a task."""
    if not verify_uuid(uuid_text):
        raise ValidationError(
            "There was an issue wiht the Task UUID validation.",
            uuid_text,
            "uuid_text",
        )
    if not verify_task_uuid_exists(uuid_text):
        raise ValidationError(
            "There was an issue wiht the Task UUID validation.",
            uuid_text,
            "uuid_text",
        )
    return True


@validation_exception_manager
def is_valid_decision(answer: str) -> bool:
    """Returns True if the answer is (y) or (n)."""
    error_message = "It should be only (y) or (n)."
    if answer != "y" and answer != "n":
        raise ValidationError(error_message, str(answer), "uuid_text")
    return True


@validation_exception_manager
def is_valid_task_status(status: str) -> bool:
    """Returns True if the status is (t), (p) or (d)."""
    error_message = "It should be only (t), (p) or (d)."
    if status != "t" and status != "p" and status != "d":
        raise ValidationError(error_message, str(status), "uuid_text")
    return True


# ////// One Parameter Validation functions for argparse types \\\\\\ #


def is_valid_not_existing_name_arg(name: str) -> str:
    """Argparse type function for validating a not registered name."""
    if is_valid_not_existing_name(name):
        return name
    else:
        raise argparse.ArgumentTypeError(
            f"Introduce an alphanumeric name of {USERNAME_LENGTH} characters."
        )


def is_valid_pass_arg(password: str) -> str:
    """Argparse type function for validating a password."""
    if is_valid_pass(password):
        return password
    else:
        raise argparse.ArgumentTypeError(
            f"Introduce an alphanumeric password of {PASSWORD_LENGTH} characters."
        )


def is_valid_name_arg(password: str) -> str:
    """Argparse type function for validating a user name."""
    if is_valid_name(password):
        return password
    else:
        raise argparse.ArgumentTypeError(
            f"Introduce an alphanumeric name of {USERNAME_LENGTH} characters."
        )


def is_valid_title_arg(password: str) -> str:
    """Argparse type function for validating a task title."""
    if is_valid_title(password):
        return password
    else:
        raise argparse.ArgumentTypeError(
            f"Introduce the task Title of ({TASK_TITLE_LENGTH}) lenght."
        )


def is_valid_description_arg(password: str) -> str:
    """Argparse type function for validating a task description."""
    if is_valid_description(password):
        return password
    else:
        raise argparse.ArgumentTypeError(
            f"Introduce the task Description ({TASK_DESCRIPTION_LENGTH}) lenght."
        )


def verify_task_uuid_arg(password: str) -> str:
    """Argparse type function for validating a task UUID."""
    if verify_task_uuid(password):
        return password
    else:
        raise argparse.ArgumentTypeError("Introduce the task UUID to edit.")


def is_valid_task_status_arg(password: str) -> str:
    """Argparse type function for validating a task status."""
    if is_valid_task_status(password):
        return password
    else:
        raise argparse.ArgumentTypeError(
            f"Introduce the task status ({TASK_STATUSES['todo']}: t, \
                {TASK_STATUSES['pending']}: p, {TASK_STATUSES['done']}: d)."
        )


# ////// Others \\\\\\ #


@validation_exception_manager
def hash_word(word: str) -> Any:
    """Returns a hashed word."""
    try:
        return hasher.hash(word)
    except ValueError:
        raise PasswordAuthenticationError("The password shold be a string.")
    except TypeError:
        raise PasswordAuthenticationError(
            "The password is too short or too long."
        )


@validation_exception_manager
def verify_hashed_word(word: str, stored_hash: str) -> bool:
    """Returns True if the hashed word is the same as the stored one."""
    try:
        if hasher.verify(stored_hash, word):
            return True
        else:
            raise VerifyMismatchError
    except VerifyMismatchError:
        raise PasswordAuthenticationError("The password is incorrect.")
