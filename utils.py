import uuid
from typing import Any

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

import data_management


USERNAME_LENGTH = 6
PASSWORD_LENGTH = 8
TASK_TITLE_LENGTH = 20
TASK_DESCRIPTION_LENGTH = 60

state = data_management.getPersistentdata()
hasher = PasswordHasher()


### Decorators ###

def verifyCurrentUser(func):
    '''Decorator to verify if there is a user currently loged.
    If there's not current session it doesn't execute the function.'''
    def wrapper():
        if state['current_user'] != None:
            func()
        else:
            print('First login please.')
    return wrapper


### Inner validation funcrtions ###


def is_alnum_with_spaces(text: str) -> bool:
    '''Returns True if the string is a group of spaced proper words.'''
    return all(char.isalnum() or char.isspace() for char in text)


def isValidText(value: str, param_name: str, is_one_word: bool) -> bool:
    '''Returns True if value is a string and it's a propper text,
    excluding spaces if is_one_word is True.'''
    try:
        valid = True
        if type(value) != str:
            print(f'{param_name} should be a string.')
            valid = False
        if is_one_word:
            if not value.isalnum():
                print(f'{param_name} should contain only letters and numbers.')
                valid = False
        else:
            if not is_alnum_with_spaces(value):
                print(f'{param_name} should contain only letters and numbers.')
                valid = False
        return valid
    except Exception as e:
        print(f'Error: {e}')
        return False


def isLongerThan(value: str, param_name: str, long: int) -> bool:
    '''Returns True if the text lenght is longer than the requested long.'''
    if len(value) >= long:
        return  True
    else:
        print(f'{param_name} should be at least {long} characters long.')
        return False


def isLessThan(value: str, param_name: str, long: int) -> bool:
    '''Returns True if the text lenght is less or equal than the requested long'''
    if len(value) <= long:
        return  True
    else:
        print(f'{param_name} should be {long} characters long maximum')
        return False


def isValidWord(value: str, param_name: str, long: int) -> bool:
    '''Returns True if the value is propper word and it's lenght is longer
    than the requested long.'''
    try:
        valid = True
        valid = isValidText(value, param_name, True)
        valid = isLongerThan(value, param_name, long)
        return valid
    except Exception as e:
        print(f'Error: {e}')
        return False


def isValidSentence(value: str, param_name: str, long: int) -> bool:
    '''Returns True if the value is propper text with spaces and it's 
    lenght is less than the requested long.'''
    try:
        valid = True
        valid = isValidText(value, param_name, False)
        valid = isLessThan(value, param_name, long)
        return valid
    except Exception as e:
        print(f'Error: {e}')
        return False


def validateUserExists(name: str) -> bool:
    '''Returns True if the username exists and it's registered.'''
    userExists = state['userset'].userExists(name) if state['userset'] != None else False
    if userExists:
        print("Username already exists.")
        return True
    else:
        return False


def verifyTaskUuidExists(uuid_text: str) -> bool:
    '''Returns True if the Task UUID is used in an actual Task object in the Task Set.'''
    try:
        task = state['taskset'].getTaskByUuid(uuid_text)
        if task is None:
            print("The Task UUID is not registered.")
            return False
        else:
            return True
    except Exception as e:
        print(f"Error: {e}")
        return False


def verifyUuid(uuid_text: str) -> bool:
    '''Returns True if the uuid in text is valid.'''
    try:
        uuid.UUID(uuid_text, version=4)
        return True
    except Exception as e:
        print(f"The Task UUID is not valid. {e}")
        return False


### One Parameter Validation functions for askData ###


def isValidTitle(title: str) -> bool:
    '''Returns True if the title is a proper sentences validating the lenght.'''
    return isValidSentence(title, 'Title', TASK_TITLE_LENGTH)


def isValidDescription(description: str) -> bool:
    '''Returns True if the description is a proper sentences validating the lenght.'''
    return isValidSentence(description, 'Description', TASK_DESCRIPTION_LENGTH)


def isValidName(name: str, validate_existence: bool = True) -> bool:
    '''Returns True if the name is a propper word,
    checks if it's not used if validate_existence is True'''
    if validate_existence and validateUserExists(name):
        print("Username already exists.")
        return False
    return isValidWord(name, 'Name', USERNAME_LENGTH)


def isValidExistingName(name: str) -> bool:
    '''Returns True if the name is a propper word, it suppose it already exists.'''
    return isValidName(name, False)


def isValidPass(password: str) -> bool:
    '''Returns True if the password is a propper word.'''
    return isValidWord(password, 'Password', PASSWORD_LENGTH)


def verifyTaskUuid(uuid_text: str) -> bool:
    '''Returns True if the uuid in text is valid and if it's used in a task.'''
    try:
        valid = verifyUuid(uuid_text)
        valid = verifyTaskUuidExists(uuid_text)
        return valid
    except Exception as e:
        print(f"There was an issue wiht the Task UUID validation. {e}")
        return False


def isValidDecision(answer: str) -> bool:
    '''Returns True if the answer is (y) or (n).'''
    return answer == 'y' or answer == 'n'


def isValidTaskStatus(status: str) -> bool:
    '''Returns True if the status is (t), (p) or (d).'''
    return status in ('t', 'p', 'd')


### Others ###


def hashWord(word: str) -> Any:
    '''Returns a hashed word.'''
    return hasher.hash(word)


def verifyHashedWord(word: str, stored_hash: str) -> bool:
    '''Returns True if the hashed word is the same as the stored one.'''
    try:
        if hasher.verify(stored_hash, word):
            return True
        else:
            return False
    except VerifyMismatchError:
        print("Password is incorrect.")
    except Exception as e:
        print(f"Error: {e}")
