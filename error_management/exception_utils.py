import functools
from typing import Any

from error_management.exceptions import ValidationError, PasswordAuthenticationError, DataError
from logging_utils import get_logger
logger = get_logger(__name__)


def validation_exception_manager(func) -> Any:
    '''
    Decorator for catching exceptions of validation type.
    If there's an exception it will return False.
    It should be used only with validation functions that return a bool.
    '''
    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        try:
            return func(*args, **kwargs)
        except ValidationError as ve:
            print(f" *********** ValidationError")
            logger.warning(f"{func.__name__} ValidationError: {ve}")
            return False
        except PasswordAuthenticationError as pe:
            logger.warning(f"{func.__name__} PasswordAuthenticationError: {pe}")
            return False
        except Exception as e:
            print(f" *********** ValidationError")
            logger.error(f"{func.__name__} Unknown Error: {e}")
            return False
    return wrapper


def data_object_exception_manager(func) -> Any:
    '''
    Decorator for catching exceptions of data object type.
    If there's an exception it will not return nothing, an error here will
    interrup the system.
    It should be used only the base models.
    '''
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs) -> Any:
        calling_class = type(self).__name__
        orignal_class = type(self).__bases__[0].__name__
        error_location = f"{orignal_class}.{func.__name__} ({calling_class})"
        try:
            return func(self, *args, **kwargs)
        except TypeError as te:
            raise TypeError(f"{error_location} TypeError: {te}")
        except AttributeError as at:
            raise AttributeError(f"{error_location} AttributeError: {at}")
        except KeyError as ke:
            raise TypeError(f"{error_location} KeyError: The key should be type str, {ke}") 
        except Exception as e:
            raise DataError(f"{error_location} DataError: {e}")
    return wrapper
