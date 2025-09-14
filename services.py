import data_management
from models import TASK_STATUSES
from utils import validateUserExists, hashWord, verifyHashedWord


state = data_management.getPersistentdata()


### User Functions ###


def createNewUser(name: str, password: str) -> None:
    '''Gets name and password and creates a new user.'''
    hashed_password = hashWord(password)
    data = {
        "name": name,
        "password": hashed_password
    }
    if not validateUserExists(name):
        state['userset'].addJSON(data)
    login(name, password)


def login(username: str, password: str) -> None:
    '''Gets name and password and updates the session with the user.'''
    user = state['userset'].getUserByName(username)
    if user is not None:
        stored_password = user.getData()['password']
        if verifyHashedWord(password, stored_password):
            state['current_user'] = user
            print(f'Logged as "{username}"')
        else:
            print("The password is not correct.")    
    else:
        print("The username doesn't exist.")


def logout() -> None:
    '''Restores the current user to None and closes the session.'''
    state['current_user'] = None
    print("User Logout.")


### Task Functions ###


def listUserTasks() -> None:
    '''Prints all the tasks created by the current user.'''
    user_uuid = state['current_user'].getUserUuid()
    user_tasks = state['taskset'].getUserTasks(user_uuid)
    [print(task) for task in user_tasks]


def createTask(title: str, description: str) -> None:
    '''Creates and prints a task related to the current user.'''
    user_uuid = state['current_user'].getUserUuid()
    data = {
        'title': title,
        'description': description,
        'owner_uuid': user_uuid,
    }
    state['taskset'].addJSON(data)
    task = state['taskset'].getLastUserCreatedTask()
    print(task)


def editTask(task_uuid: str, title: str, description: str, status: str) -> None:
    '''Gets task UUID, title and description and updates the task.'''
    new_status = None
    match status:
        case 't':
            new_status = TASK_STATUSES['todo']
        case 'p':
            new_status = TASK_STATUSES['pending']
        case 'd':
            new_status = TASK_STATUSES['done']

    state['taskset'].updateTask(task_uuid, title, description, new_status)


def deleteTask(task_uuid: str) -> None:
    '''Gets task UUID and deletes the task.'''
    state['taskset'].deleteTask(task_uuid)
