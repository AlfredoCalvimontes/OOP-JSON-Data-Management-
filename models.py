from  datetime import datetime, timezone
from typing import Dict, List, Set
import uuid


TASK_STATUSES = {
                 'todo': 'TODO',
                 'pending': 'PENDING',
                 'done': 'DONE'
                 }
DATETIME_FORMAT = '%Y/%m/%d, %H:%M:%S'


class DataEntity:
    filepath: str = ""

    def getData(self) -> Dict:
        return {key[1:]: value for key, value in vars(self).items()}

    def udpate(self, json: Dict) -> None:
        if isinstance(json, Dict):
            for key, value in json.items():
                new_key = f'_{key}'
                if hasattr(self, new_key):
                    setattr(self, new_key, value)
        else:
            print("TypeError: It's not a JSON.")


class User(DataEntity):
    ''''''
    filepath: str = "users.JSON"

    def __init__(self,
                 name: str,
                 password: str,
                 user_uuid: str = None,
                 deleted: bool = False,
                 creation_datetime: str = None,
                 update_datetime: str = None
                 ):
        datetime_now = datetime.now(timezone.utc).strftime(DATETIME_FORMAT)
        self._user_uuid: str = user_uuid if user_uuid != None else str(uuid.uuid4())
        self._name: str = name
        self._password: str = password
        self._deleted: str = deleted if deleted != None else False
        self._creation_datetime: str = creation_datetime if creation_datetime !=None else datetime_now
        self._update_datetime: str = update_datetime if update_datetime !=None else datetime_now

    def getUserName(self):
        return self._name
    
    def getUserUuid(self):
        return self._user_uuid


class Task(DataEntity):
    filepath: str = "tasks.JSON"

    def __init__(self,
                 title: str,
                 description: str,
                 owner_uuid: str,
                 task_uuid: str = None,
                 status: str = TASK_STATUSES['todo'],
                 deleted: str = False,
                 creation_datetime: str = None,
                 update_datetime: str = None,
                 ):
        datetime_now = datetime.now(timezone.utc).strftime(DATETIME_FORMAT)
        self._task_uuid: str = task_uuid if task_uuid != None else str(uuid.uuid4())
        self._title: str = title
        self._description: str = description
        self._status: str = status if status != None else TASK_STATUSES['todo']
        self._deleted: str = deleted if deleted != None else False
        self._creation_datetime: str = creation_datetime if creation_datetime !=None else datetime_now
        self._update_datetime: str = update_datetime if update_datetime !=None else datetime_now
        self._owner_uuid: str = owner_uuid

    def __str__(self) -> None:
        return self.to_string(include_dates=True)

    def to_string(self,
              include_deleted: bool = False,
              include_user: bool = False,
              include_dates: bool = False
              ) -> None:
        deleted_line = f"\n        ---- {self._deleted} ----"
        add_deleted = deleted_line if self._deleted != None or self._deleted == False else ''
        add_deleted = deleted_line if include_deleted == True else add_deleted

        dates_lines = f'''
        °°°° Created at: {self._creation_datetime}
        °°°° Updated at: {self._update_datetime}
        '''
        add_dates = dates_lines if include_dates == True else ''

        user_line = f"\n---- User: {self._owner_uuid}"
        add_user = user_line if include_user == True else ''

        text = f'''
        ------------------------------------------------
        ------------------------------------------------
        |||| {self._title} ||||
        ---- {self._status} ----
        ---- UUID: {self._task_uuid} ----{add_deleted}
        {self._description}{add_dates}{add_user}
        '''
        return text


class DataEntitySet(Set):
    ''''''
    related_class = DataEntity

    def __init__(self, jsonList: List = None) -> None:
        if jsonList is not None:
            for data_entity in jsonList:
                self.addJSON(data_entity)
        else:
            return super().__init__()

    def add(self, data_entity: DataEntity) -> None:
        if isinstance(data_entity, self.related_class):
            super().add(data_entity)
        else:
            print(f"TypeError: The item should be type {self.related_class}")

    def update(self, dataEntities: Set) -> None:
        filtered_dataEntities = [data_entity for data_entity in dataEntities if isinstance(data_entity, self.related_class)]
        super().update(filtered_dataEntities)

    def addJSON(self, json: Dict) -> None:
        if isinstance(json, Dict):
            attributes = {attr[1:]: json.get(attr[1:], None)
                          for attr in self.related_class.__dict__['__static_attributes__']}
            data_entity = self.related_class(**attributes)
            self.add(data_entity)
        else:
            print("TypeError: It's not a JSON.")

    def getDataEntityByKey(self, key: str, value: str) -> DataEntity:
        for data_entity in self:
            if data_entity.getData()[key] == value:
                return data_entity
        return None

    def getDataEntityByUuid(self, uuid: str) -> DataEntity:
        class_name = self.related_class.__name__.lower()
        return self.getDataEntityByKey(f'{class_name}_uuid', uuid)
    
    def getFilteredEntities(self, key_values: Dict) -> Set:
        return {
            item for key in key_values.keys()
            for item in self
            if item.getData().get(f"_{key}", None) == key_values[key]
            }
    
    def dump(self) -> List[Dict]:
        return [data_entity.getData() for data_entity in self]

    def remove(self):
        print("TypeError: You can't remove by value.")

    def discard(self):
        print("TypeError: You can't discard by value.")

    def pop(self):
        print("TypeError: You can't pop a data entity.")

    def clear(self):
        print("TypeError: You can't clear the data entity set.")


class UserSet(DataEntitySet):
    related_class = User

    def __init__(self, jsonList: List = None):
        super().__init__(jsonList)

    def getUserByKey(self, key: str, value: str) -> User:
        return super().getDataEntityByKey(key, value)

    def getUserByUuid(self, uuid: str) -> User:
        return super().getDataEntityByUuid(uuid)

    def getUserByName(self, name: str) -> User:
        return self.getUserByKey('name', name)

    def userExists(self, name: str) -> bool:
        return True if self.getUserByName(name) != None else False


class TaskSet(DataEntitySet):
    related_class = Task

    def __init__(self, jsonList: List = None):
        super().__init__(jsonList)

    def getTaskByKey(self, key: str, value: str) -> Task:
        return super().getDataEntityByKey(key, value)

    def getTaskByUuid(self, uuid: str) -> Task:
        return super().getDataEntityByUuid(uuid)
    
    def getUserTasks(self, owner_uuid: str, filter_status: str = None, inclue_delete: bool = False) -> Set:
        filter_data = {'owner_uuid': owner_uuid}
        filter_data['status'] = filter_status if filter_status != None else None
        filter_data['deleted'] = False if inclue_delete else None
        return super().getFilteredEntities(filter_data)

    def getLastUserCreatedTask(self) -> related_class:
        return max(self, key=lambda task: task.getData()['creation_datetime'])
    
    def deleteTask(self, uuid_text: str) -> None:
        task = self.getTaskByUuid(uuid_text)
        datetime_now = datetime.now(timezone.utc).strftime(DATETIME_FORMAT)
        task.udpate({
            'deleted': True,
            'update_datetime': datetime_now
            })

    def updateTask(self, uuid_text: str, title: str, description: str, status: str) -> None:
        task = self.getTaskByUuid(uuid_text)
        datetime_now = datetime.now(timezone.utc).strftime(DATETIME_FORMAT)
        task.udpate({
            'title': title,
            'description': description,
            'update_datetime': datetime_now,
            'status': status
            })
