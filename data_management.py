import json
from typing import Any, Dict

from config import FILEPATH
from constants import OPERATIONS
from error_management.exceptions import FileError
from logging_utils import get_logger
from models import DataEntitySet


logger = get_logger(__name__)
# We use a state here becouse a dictinary maintain the references, not copies.
# It stores the data on sets of objects.
state: dict[str, Any] = {
    "current_user": {"user": None, "loged_in_datetime": None}
}


def data_object_loading(
    object_path: str, operation: str, data: Any = None
) -> Any:
    """
    Gets the file and returns the data or gets the data
    and stores it into the file.
    """
    try:
        path = str(FILEPATH) + object_path
        with open(path, operation) as file:
            if operation == "r":
                return json.load(file)
            if operation == "w" and data is not None:
                json.dump(data, file, indent=4, sort_keys=True)
            else:
                raise FileError("Operation not defined.")
    except FileNotFoundError as fnfe:
        logger.warning(
            f"data_object_loading: FileNotFoundError: \
                The file at '{path}' was not found. {fnfe}"
        )
        return None
    except json.JSONDecodeError as jse:
        logger.warning(
            f"data_object_loading: JSONDecodeError: \
                The file at '{path}' is not a valid JSON file. {jse}"
        )
        return None
    except FileError as fe:
        logger.warning(
            f"data_object_loading: FileError: \
                There was an issue working with files. {fe}"
        )
        return None
    except Exception as e:
        logger.error(
            f"data_object_loading: Error: \
                An unexpected error occurred when retrieven the JSON file: {e}"
        )
        return None


def get_sets_and_object() -> Dict:
    """Returns a dictionary with the sets as keys the objects as values."""
    try:
        dataEntitySets = DataEntitySet.__subclasses__()
        return {
            key: value
            for key, value in zip(
                dataEntitySets,
                [
                    dataEntitySet.related_class
                    for dataEntitySet in dataEntitySets
                ],
            )
        }
    except Exception as e:
        logger.error(
            f"Error in getSetsAndObject, returned an empty dictionary: {e}"
        )
        return {}


def data_loading() -> None:
    """Loads the data from the files into the sets of objects."""
    try:
        logger.info("Loading data...")
        sets_and_objects = get_sets_and_object()
        # Left a separated for because it's more readable
        for data_set, object in sets_and_objects.items():
            state[data_set.__name__.lower()] = data_set(
                data_object_loading(object.filepath, OPERATIONS["reading"])
            )
        logger.info("Finished loading data.")
    except Exception as e:
        logger.error(f"data_loading: Error: {e}")


def data_saving() -> None:
    """Storages the data from the sets of objects into the files."""
    try:
        logger.info("Saving data...")
        sets_and_objects = get_sets_and_object()
        # Left a separated for because it's more readable
        for data_set, object in sets_and_objects.items():
            dataset: DataEntitySet = state[data_set.__name__.lower()]
            data_object_loading(
                object.filepath, OPERATIONS["writing"], dataset.dump()
            )
        logger.info("Finished saving data.")
    except Exception as e:
        logger.error(f"data_saving: Error: {e}")


def get_persistent_data() -> Dict:
    """Returns the state with all the sets of data and the current user."""
    return state
