import data_management
from constants import TASK_STATUSES
from utils import validate_user_not_exists, hash_word, verify_hashed_word


state = data_management.get_persistent_data()


# ////// User Functions \\\\\\ #


def create_new_user(name: str, password: str) -> None:
    """Gets name and password and creates a new user."""
    hashed_password = hash_word(password)
    data = {"name": name, "password": hashed_password}
    if validate_user_not_exists(name):
        state["userset"].add_jSON(data)
    login(name, password)


def login(username: str, password: str) -> None:
    """Gets name and password and updates the session with the user."""
    user = state["userset"].get_user_by_name(username)
    if user is not None:
        stored_password = user.get_data()["password"]
        if verify_hashed_word(password, stored_password):
            state["current_user"] = user
            print(f'Logged as "{username}"')  # TODO: Logg or argparse
        else:
            print("The password is not correct.")  # TODO: Logg or argparse
    else:
        print("The username doesn't exist.")  # TODO: Logg or argparse


def logout() -> None:
    """Restores the current user to None and closes the session."""
    state["current_user"] = None
    print("User Logout.")  # TODO: Logg or argparse


# ////// Task Functions \\\\\\ #


def list_user_tasks() -> None:
    """Prints all the tasks created by the current user."""
    user_uuid = state["current_user"].get_user_uuid()
    user_tasks = state["taskset"].get_user_tasks(user_uuid)
    [print(task) for task in user_tasks]  # TODO: Logg or argparse


def create_task(title: str, description: str) -> None:
    """Creates and prints a task related to the current user."""
    user_uuid = state["current_user"].get_user_uuid()
    data = {
        "title": title,
        "description": description,
        "owner_uuid": user_uuid,
    }
    state["taskset"].add_jSON(data)
    task = state["taskset"].get_last_user_created_task()
    print(task)  # TODO: Logg or argparse


def edit_task(
    task_uuid: str, title: str, description: str, status: str
) -> None:
    """Gets task UUID, title and description and updates the task."""
    new_status = None
    match status:
        case "t":
            new_status = TASK_STATUSES["todo"]
        case "p":
            new_status = TASK_STATUSES["pending"]
        case "d":
            new_status = TASK_STATUSES["done"]

    state["taskset"].update_task(task_uuid, title, description, new_status)


def delete_task(task_uuid: str) -> None:
    """Gets task UUID and deletes the task."""
    state["taskset"].delete_task(task_uuid)
