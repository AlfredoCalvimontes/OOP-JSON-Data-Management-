import sys
from typing import List

import data_management
from constants import TASK_STATUSES
from services import create_new_user, create_task, delete_task, edit_task, list_user_tasks, login, logout
from utils import (is_valid_decision, is_valid_description, is_valid_name, is_valid_not_existing_name,\
                   is_valid_pass, is_valid_task_status, is_valid_title, PASSWORD_LENGTH, TASK_DESCRIPTION_LENGTH,\
                   TASK_TITLE_LENGTH, USERNAME_LENGTH, verify_current_user, verify_task_uuid)


state = data_management.get_persistent_data()



def ask_data(items: List) -> List:
    ''' 
    It get all the listed data and validate it.
    It iterates though each item and calls the validation function
    with the intriduced value to validate the data.
    The function in the dictionary should request only one value.
    items Example:
    List format: [{
                    "message": "example message",
                    "validation_function": func(one_value)
                 }]
    '''
    result = []

    for item in items:
        valid = False
        value = None
        while not valid:
            value = input(item['message'])
            valid = item['validation_function'](value)
        result.append(value)
    return result


def welcome() -> None:
    '''It prints a welcoming message.'''
    print('''
          Welcome to Task Manager 20000!
          We hope you are having a great experince.
          ''')


def create_new_user_action() -> None:
    '''Asks for name and password and creates a new user.'''
    items = [
        {
            "message": f"Introduce an alphanumeric name of {USERNAME_LENGTH} characters: ",
            "validation_function": is_valid_not_existing_name
        },
        {
            "message": f"Introduce an alphanumeric password of {PASSWORD_LENGTH} characters: ",
            "validation_function": is_valid_pass
        }
            ]

    name, password = ask_data(items)
    create_new_user(name, password)


def login_action() -> None:
    '''Asks for username and password and register it in the session.'''
    items = [
        {
            "message": "Introduce your username: ",
            "validation_function": is_valid_name
        },
        {
            "message": "Introduce your password: ",
            "validation_function": is_valid_pass
        }
            ]

    name, password = ask_data(items)
    login(name, password)


def logout_action() -> None:
    '''Restores the current user to None and close the session.'''
    logout()


@verify_current_user
def list_user_tasks_action() -> None:
    '''Prints the list of all tasks the user created.'''
    list_user_tasks()


@verify_current_user
def create_taskAction() -> None:
    '''Asks for title and description and creates a new task.'''
    items = [
        {
            "message": f"Introduce the task Title ({TASK_TITLE_LENGTH}): ",
            "validation_function": is_valid_title
        },
        {
            "message": f"Introduce the task Description ({TASK_DESCRIPTION_LENGTH}): ",
            "validation_function": is_valid_description
        }
            ]
    title, description = ask_data(items)
    create_task(title, description)


@verify_current_user
def edit_task_action() -> None:
    '''Asks for the task UUID, title and description and updates the task.'''
    items = [
        {
            "message": f"Introduce the task UUID to edit: ",
            "validation_function": verify_task_uuid
        },
        {
            "message": f"Introduce the task Title ({TASK_TITLE_LENGTH}): ",
            "validation_function": is_valid_title
        },
        {
            "message": f"Introduce the task Description ({TASK_DESCRIPTION_LENGTH}): ",
            "validation_function": is_valid_description
        },
        {
            "message": f"Introduce the task status ({TASK_STATUSES['todo']}: t, {TASK_STATUSES['pending']}: p,\
 {TASK_STATUSES['done']}: d): ",
            "validation_function": is_valid_task_status
        }
            ]
    task_uuid, title, description, status = ask_data(items)
    edit_task(task_uuid, title, description, status)


@verify_current_user
def delete_task_action() -> None:
    '''Asks for the task UUID, verify the decision and deletes the task.'''
    items = [
        {
            "message": f"Introduce the task UUID to edit: ",
            "validation_function": verify_task_uuid
        },
        {
            "message": f"Sure? (y) Yes (n) No: ",
            "validation_function": is_valid_decision
        }
            ]
    task_uuid, answer = ask_data(items)
    if answer:
        delete_task(task_uuid)


def exitAction():
    '''Closes the app and stores the data.'''
    data_management.data_saving()
    sys.exit()


MENU_ITEMS = [
    ('Create new User', create_new_user_action),
    ('Login', login_action),
    ('Logout', logout_action),
    ('Create Task', create_taskAction),
    ('List your tasks', list_user_tasks_action),
    ('Edit task', edit_task_action),
    ('Delete task', delete_task_action),
    ('Exit', exitAction),
]


def generate_menu() -> str:
    '''Generates the menu text using the MENU_ITEMS list.'''
    menu_text = ''
    for index, menu_entry in enumerate(MENU_ITEMS, 1):
        menu_text += f"           [{index}]: {menu_entry[0]}\n"
    return menu_text


def main_menu() -> None:
    '''Presents and iterates the menu.'''
    while True:
        username = None if state['current_user'] == None else state['current_user'].get_user_name()
        print(f'''
        Task Manager 20000 { f'/// User: {username}' if username != None else ' '}
        Choose an option:\n{generate_menu()}
        ''')
        selected_option = input()
        if selected_option.isdigit() and int(selected_option) >= 1 and int(selected_option) <= 8:
            MENU_ITEMS[int(selected_option)-1][1]()
