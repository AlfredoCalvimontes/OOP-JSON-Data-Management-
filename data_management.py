import json
from typing import Any, Dict

from models import DataEntitySet


FILEPATH = "data/"
USERS_PATH = "users.JSON"
TASK_PATH = "tasks.JSON"
OPERATIONS = {
    'reading': 'r',
    'writing': 'w',
    'reading_and_writing': 'r',
}

# We use a state here becouse a dictinary maintain the references, not copies.
# It stores the data on sets of objects.
state = {
    'current_user': None
}


def dataObjectLoading(object_path: str, operation: str, data: Any = None) -> Any:
    '''Gets the file and returns the data or gets the data and stores it into the file.'''
    try:
        path = FILEPATH + object_path
        with open(path, operation) as file:
            if operation == 'r':
                return json.load(file)
            if operation == 'w' and data != None: 
                json.dump(data, file, indent=4, sort_keys=True)
    except FileNotFoundError:
        print(f"Error: The file at '{path}' was not found.")
        return None
    except json.JSONDecodeError:
        print(f"Error: The file at '{path}' is not a valid JSON file.")
        return None
    except Exception as e:
        print(f"Error: An unexpected error occurred when retrieven the JSON file: {e}")
        return None


def getSetsAndObject() -> Dict:
    '''Returns a dictionary with the sets as keys the objects as values.'''
    dataEntitySets = DataEntitySet.__subclasses__()
    return {
        key: value for key,value
        in zip(dataEntitySets, [dataEntitySet.related_class for dataEntitySet in dataEntitySets])
        }


def dataLoading() -> None:
    '''Loads the data from the files into the sets of objects.'''
    sets_and_objects = getSetsAndObject()
    # Left a separated for because it's more readable
    for data_set, object in sets_and_objects.items():
        state[data_set.__name__.lower()] = data_set(dataObjectLoading(object.filepath, OPERATIONS['reading']))


def saveData() -> None:
    '''Storages the data from the sets of objects into the files.'''
    sets_and_objects = getSetsAndObject()
    # Left a separated for because it's more readable
    for data_set, object in sets_and_objects.items():
        dataset = state[data_set.__name__.lower()]
        dataObjectLoading(object.filepath, OPERATIONS['writing'], dataset.dump())


def getPersistentdata() -> None:
    '''Returns the state with all the sets of data and the current user.'''
    return state
