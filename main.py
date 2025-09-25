import sys

from dotenv import load_dotenv

from data_management import data_loading
from error_management.exceptions import AppError
from frontend.interface import main_menu, welcome
from frontend.arg_interface import run_command
from logging_utils import configure_logger
from session_management import load_session


def main():
    """Calls tha main initializing functions."""
    try:
        load_dotenv()
        configure_logger()
        data_loading()
        load_session()
        if len(sys.argv) > 1:
            run_command()
        else:
            welcome()
            main_menu()
    except Exception as e:
        import traceback

        detailed_traceback = traceback.format_exc()
        raise AppError(f"AppError: {e}.\n{detailed_traceback}")


if __name__ == "__main__":
    main()
