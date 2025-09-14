import sys
from typing import List

import data_management
from models import TASK_STATUSES
from services import createNewUser, createTask, deleteTask, editTask, listUserTasks, login, logout
from utils import (isValidExistingName, isValidDecision, isValidDescription, isValidName, isValidPass,\
                   isValidTaskStatus, isValidTitle, PASSWORD_LENGTH, TASK_DESCRIPTION_LENGTH,\
                   TASK_TITLE_LENGTH, USERNAME_LENGTH, verifyCurrentUser, verifyTaskUuid)


state = data_management.getPersistentdata()



def askData(items: List) -> None:
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


def createNewUserAction() -> None:
    '''Asks for name and password and creates a new user.'''
    items = [
        {
            "message": f"Introduce an alphanumeric name of {USERNAME_LENGTH} characters: ",
            "validation_function": isValidName
        },
        {
            "message": f"Introduce an alphanumeric password of {PASSWORD_LENGTH} characters: ",
            "validation_function": isValidPass
        }
            ]

    name, password = askData(items)
    createNewUser(name, password)


def loginAction() -> None:
    '''Asks for username and password and register it in the session.'''
    items = [
        {
            "message": "Introduce your username: ",
            "validation_function": isValidExistingName
        },
        {
            "message": "Introduce your password: ",
            "validation_function": isValidPass
        }
            ]

    name, password = askData(items)
    login(name, password)


def logoutAction() -> None:
    '''Restores the current user to None and close the session.'''
    logout()


@verifyCurrentUser
def listUserTasksAction() -> None:
    '''Prints the list of all tasks the user created.'''
    listUserTasks()


@verifyCurrentUser
def createTaskAction() -> None:
    '''Asks for title and description and creates a new task.'''
    items = [
        {
            "message": f"Introduce the task Title ({TASK_TITLE_LENGTH}): ",
            "validation_function": isValidTitle
        },
        {
            "message": f"Introduce the task Description ({TASK_DESCRIPTION_LENGTH}): ",
            "validation_function": isValidDescription
        }
            ]
    title, description = askData(items)
    createTask(title, description)


@verifyCurrentUser
def editTaskAction() -> None:
    '''Asks for the task UUID, title and description and updates the task.'''
    items = [
        {
            "message": f"Introduce the task UUID to edit: ",
            "validation_function": verifyTaskUuid
        },
        {
            "message": f"Introduce the task Title ({TASK_TITLE_LENGTH}): ",
            "validation_function": isValidTitle
        },
        {
            "message": f"Introduce the task Description ({TASK_DESCRIPTION_LENGTH}): ",
            "validation_function": isValidDescription
        },
        {
            "message": f"Introduce the task status ({TASK_STATUSES['todo']}: t, {TASK_STATUSES['pending']}: p,\
 {TASK_STATUSES['done']}: d): ",
            "validation_function": isValidTaskStatus
        }
            ]
    task_uuid, title, description, status = askData(items)
    editTask(task_uuid, title, description, status)


@verifyCurrentUser
def deleteTaskAction() -> None:
    '''Asks for the task UUID, verify the decision and deletes the task.'''
    items = [
        {
            "message": f"Introduce the task UUID to edit: ",
            "validation_function": verifyTaskUuid
        },
        {
            "message": f"Sure? (y) Yes (n) No: ",
            "validation_function": isValidDecision
        }
            ]
    task_uuid, answer = askData(items)
    if answer:
        deleteTask(task_uuid)


def exitAction():
    '''Closes the app and stores the data.'''
    data_management.saveData()
    sys.exit()


MENU_ITEMS = [
    ('Create new User', createNewUserAction),
    ('Login', loginAction),
    ('Logout', logoutAction),
    ('Create Task', createTaskAction),
    ('List your tasks', listUserTasksAction),
    ('Edit task', editTaskAction),
    ('Delete task', deleteTaskAction),
    ('Exit', exitAction),
]


def generateMenu() -> str:
    '''Generates the menu text using the MENU_ITEMS list.'''
    menu_text = ''
    for index, menu_entry in enumerate(MENU_ITEMS, 1):
        menu_text += f"           [{index}]: {menu_entry[0]}\n"
    return menu_text


def main_menu() -> None:
    '''Presents and iterates the menu.'''
    while True:
        username = None if state['current_user'] == None else state['current_user'].getUserName()
        print(f'''
        Task Manager 20000 { f'/// User: {username}' if username != None else ' '}
        Choose an option:\n{generateMenu()}
        ''')
        selected_option = input()
        if selected_option.isdigit() and int(selected_option) >= 1 and int(selected_option) <= 8:
            MENU_ITEMS[int(selected_option)-1][1]()
