from datetime import datetime, timezone, timedelta

import data_management
from constants import (
    CURRENT_USER_PATH,
    DATETIME_FORMAT,
    OPERATIONS,
    SESSION_TIME,
)
from error_management.exceptions import SessionError
from logging_utils import get_logger
from models import User


logger = get_logger(__name__)
state = data_management.get_persistent_data()


def verify_session_time_expired(loged_in_datetime: str) -> bool:
    print(" ******* verify_session_time_expired called")
    """Verifies if the session time is expired."""
    current_time = datetime.now(timezone.utc)
    print(f" ******* loged_in_datetime: {loged_in_datetime}")
    if loged_in_datetime is not None:
        logged_in_dt = datetime.strptime(
            loged_in_datetime,
            DATETIME_FORMAT,
        ).replace(tzinfo=timezone.utc)
        expiration_time = logged_in_dt + timedelta(minutes=SESSION_TIME)
        print(f" ******* expiration_time: {expiration_time}")
        if current_time < expiration_time:
            print(" ******* returning False")
            return False
    print(" ******* returning True")
    return True


def verify_session_expired() -> bool:
    """Verifies if the current user session is expired."""
    print(" ******* verify_session_expired called")
    print(f" ******* state['current_user']: {state['current_user']}")
    print(
        f" ******* state['current_user']['user']: {state['current_user']['user']}"
    )
    if state["current_user"]["user"] is None:
        print(
            f" ******* state['current_user']['user']: {state['current_user']['user']}"
        )
        return True
    if state["current_user"]["loged_in_datetime"] is None:
        print(
            f" ******* state['current_user']['loged_in_datetime']: {state['current_user']['loged_in_datetime']}"
        )
        return True
    return verify_session_time_expired(
        state["current_user"]["loged_in_datetime"]
    )


def load_session() -> None:
    """Loads the current user session data."""
    try:
        current_user_data = data_management.data_object_loading(
            CURRENT_USER_PATH, OPERATIONS["reading"]
        )
        expired = verify_session_time_expired(
            current_user_data["loged_in_datetime"]
        )
        if expired is False:
            current_user = state["userset"].get_user_by_uuid(
                current_user_data["user_uuid"]
            )
            state["current_user"] = {
                "user": current_user,
                "loged_in_datetime": current_user_data["loged_in_datetime"],
            }
            print(" ******* state['current_user']: ", state["current_user"])

        else:
            logger.info("Previous session expired.")
        logger.info("Session loaded.")
    except Exception as e:
        logger.error(f"load_session: Error: {e}")


def save_session(user: User) -> None:
    """Storages the current user session data."""
    try:
        datetime_now = datetime.now(timezone.utc).strftime(DATETIME_FORMAT)
        state["current_user"]["user"] = user
        state["current_user"]["loged_in_datetime"] = datetime_now
        print(" ******* datetime_now: ", datetime_now)
        print(" ******* user.get_user_name(): ", user.get_user_name())
        data = {
            "name": user.get_user_name(),
            "user_uuid": user.get_user_uuid(),
            "loged_in_datetime": datetime_now,
        }
        data_management.data_object_loading(
            CURRENT_USER_PATH, OPERATIONS["writing"], data
        )
        logger.info("Session saved.")
    except Exception as e:
        logger.error(f"save_session: Error: {e}")


def set_defatult_session_value() -> None:
    """Sets the default value for the current user session."""
    state["current_user"] = {"user": None, "loged_in_datetime": None}


def get_session_user() -> User:
    """Returns the current user object."""
    return state["current_user"]["user"]


def verify_current_user(func):
    """
    Decorator to verify if there is a user currently loged.
    If there's not current session it doesn't execute the function.
    """

    def wrapper(*args, **kwargs):
        try:
            if not verify_session_expired():
                func(*args, **kwargs)
            else:
                raise SessionError(
                    "There's no session intialized.\nFirst login please."
                )
        except SessionError as se:
            logger.info(f"verify_current_user: {se}")
        except Exception as e:
            logger.error(f"Error: in verify_current_user: {e}")

    return wrapper
