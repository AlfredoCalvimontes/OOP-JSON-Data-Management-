from dotenv import load_dotenv

from interface import main_menu, welcome
from error_management.exceptions import AppError
from data_management import data_loading
from logging_utils import configure_logger


def main():
    """Calls tha main initializing functions."""
    try:
        load_dotenv()
        configure_logger()
        data_loading()
        welcome()
        main_menu()
    except Exception as e:
        import traceback

        detailed_traceback = traceback.format_exc()
        raise AppError(f"AppError: {e}.\n{detailed_traceback}")


if __name__ == "__main__":
    main()
