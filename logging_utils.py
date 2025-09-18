import logging
from logging import Logger

from config import ENVIRONMENT
from constants import DATETIME_FORMAT


def configure_logger() -> None:
    '''Sets the necessary settings for logger, it should be called once.'''
    level = logging.DEBUG if ENVIRONMENT == 'Development' else logging.INFO
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt=DATETIME_FORMAT
    )

    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    file_handler = logging.FileHandler('app.log', 'a')
    # Saves all logs in the file.
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    
    console_handler = logging.StreamHandler()
    # Shows all not debug logs in prod.
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)


def get_logger(logger_name: str) -> Logger:
    '''Returns a logger with the received name.'''
    return logging.getLogger(logger_name)
