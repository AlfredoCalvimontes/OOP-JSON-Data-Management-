import sys
import argparse

import data_management
from constants import (
    TASK_STATUSES,
    USERNAME_LENGTH,
    PASSWORD_LENGTH,
    TASK_TITLE_LENGTH,
    TASK_DESCRIPTION_LENGTH,
)
from services import (
    create_new_user,
    create_task,
    delete_task,
    edit_task,
    list_user_tasks,
    login,
    logout,
)
from session_management import verify_session_expired
from utils import (
    is_valid_description_arg,
    is_valid_name_arg,
    is_valid_not_existing_name_arg,
    is_valid_pass_arg,
    is_valid_task_status_arg,
    is_valid_title_arg,
    verify_task_uuid_arg,
)


state = data_management.get_persistent_data()


def create_paser() -> argparse.ArgumentParser:
    """Creates the argument parser and subparsers for each command."""
    parser = argparse.ArgumentParser(
        prog="task_manager", description="Task Manager 20000 CLI"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Create users command group
    users_parser = subparsers.add_parser("users", help="Manage user commands")
    users_subparsers = users_parser.add_subparsers(
        dest="user_command", required=True, help="Users subcommands"
    )

    # Create user
    parser_create_user = users_subparsers.add_parser(
        "create", help="Create a new user", aliases=["add"]
    )
    parser_create_user.add_argument(
        "-n",
        "--name",
        dest="name",
        required=True,
        type=is_valid_not_existing_name_arg,
        help=f"Alphanumeric name of {USERNAME_LENGTH} characters",
    )
    parser_create_user.add_argument(
        "-p",
        "--password",
        dest="password",
        required=True,
        type=is_valid_pass_arg,
        help=f"Alphanumeric password of {PASSWORD_LENGTH} characters",
    )

    # Login
    parser_login = users_subparsers.add_parser(
        "login", help="Login as a user", aliases=["log"]
    )
    parser_login.add_argument(
        "-n",
        "--name",
        dest="name",
        required=True,
        type=is_valid_name_arg,
        help="Username",
    )
    parser_login.add_argument(
        "-p",
        "--password",
        dest="password",
        required=True,
        type=is_valid_pass_arg,
        help="Password",
    )

    # Logout
    parser_login = users_subparsers.add_parser(
        "logout", help="Logout current user", aliases=["lout"]
    )

    # Create tasks command group
    tasks_parser = subparsers.add_parser("tasks", help="Manage task commands")
    tasks_subparsers = tasks_parser.add_subparsers(
        dest="task_command", required=True, help="Tasks subcommands"
    )

    # List tasks
    tasks_subparsers.add_parser(
        "list-tasks", help="List your tasks", aliases=["list"]
    )

    # Create task
    parser_create_task = tasks_subparsers.add_parser(
        "create-task", help="Create a new task", aliases=["add"]
    )
    parser_create_task.add_argument(
        "-t",
        "--title",
        dest="title",
        required=True,
        type=is_valid_title_arg,
        help=f"Task title ({TASK_TITLE_LENGTH})",
    )
    parser_create_task.add_argument(
        "-d",
        "--description",
        dest="description",
        required=True,
        type=is_valid_description_arg,
        help=f"Task description ({TASK_DESCRIPTION_LENGTH})",
    )

    # Edit task
    parser_edit_task = tasks_subparsers.add_parser(
        "edit-task", help="Edit a task", aliases=["mod"]
    )
    parser_edit_task.add_argument(
        "-id",
        "--uuid",
        dest="uuid",
        required=True,
        type=verify_task_uuid_arg,
        help="Task UUID to edit",
    )
    parser_edit_task.add_argument(
        "-t",
        "--title",
        dest="title",
        required=True,
        type=is_valid_title_arg,
        help=f"Task title ({TASK_TITLE_LENGTH})",
    )
    parser_edit_task.add_argument(
        "-d",
        "--description",
        dest="description",
        required=True,
        type=is_valid_description_arg,
        help=f"Task description ({TASK_DESCRIPTION_LENGTH})",
    )
    parser_edit_task.add_argument(
        "-s",
        "--status",
        dest="status",
        required=True,
        type=is_valid_task_status_arg,
        choices=list(TASK_STATUSES.values()),
        help=f"Task status: {', '.join(TASK_STATUSES.values())}",
    )

    # Delete task
    parser_delete_task = tasks_subparsers.add_parser(
        "delete-task", help="Delete a task", aliases=["del"]
    )
    parser_delete_task.add_argument(
        "-id",
        "--uuid",
        dest="uuid",
        required=True,
        type=verify_task_uuid_arg,
        help="Task UUID to delete",
    )

    return parser


def define_command_args(parser: argparse.ArgumentParser) -> None:
    """Decides the correct command."""

    args = parser.parse_args()

    match args.command:
        case "users":
            match args.user_command:
                case "create" | "add":
                    create_new_user(args.name, args.password)
                case "login" | "log":
                    login(args.name, args.password)
                case "logout" | "lout":
                    logout()
                case _:
                    print("Unrecognized user subcommand.")
        case "tasks":
            match args.task_command:
                case "list-tasks" | "list":
                    if verify_session_expired():
                        print("No user logged in.")
                        sys.exit(1)
                    list_user_tasks()
                case "create-task" | "add":
                    print(" *********** ")
                    if verify_session_expired():
                        print("No user logged in.")
                        sys.exit(1)
                    create_task(args.title, args.description)
                    print("Task created.")
                case "edit-task" | "mod":
                    if verify_session_expired():
                        print("No user logged in.")
                        sys.exit(1)
                    edit_task(
                        args.uuid, args.title, args.description, args.status
                    )
                    print("Task edited.")
                case "delete-task" | "del":
                    if verify_session_expired():
                        print("No user logged in.")
                        sys.exit(1)
                    confirm = (
                        input(
                            "Are you sure you want to delete this task? (y/n): "
                        )
                        .strip()
                        .lower()
                    )
                    if confirm != "y":
                        print("Deletion cancelled.")
                        sys.exit(0)
                    delete_task(args.uuid)
                case _:
                    print("Unrecognized task subcommand.")
        case _:
            print("This command is not recognized.")


def run_command() -> None:
    """Run the command line interface and returs True if one was excecuted."""
    parser = create_paser()
    define_command_args(parser)
