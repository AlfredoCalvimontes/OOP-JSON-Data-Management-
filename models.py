from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Set, Type
import uuid

from constants import DATETIME_FORMAT, TASK_STATUSES
from error_management.exceptions import (
    UserError,
    TaskError,
    TaskSetError,
    UserSetError,
)
from error_management.exception_utils import data_object_exception_manager


class DataEntity:
    """
    Entity that allows it's childer with data get dynamically it's attributes
    and updated them dynamically too. It's used to load and contain \
    corresponding JSON objects defined in the filepath.
    """

    filepath: str = ""

    @data_object_exception_manager
    def __init__(self):
        super().__init__()

    @data_object_exception_manager
    def get_data(self) -> Dict:
        """
        Get a dictionary with all the attributes define in the current class.
        """
        return {key[1:]: value for key, value in vars(self).items()}

    @data_object_exception_manager
    def udpate(self, json: Dict) -> None:
        """
        Updates all the received attributes in a dictionary defined \
        in the current class.
        """
        if isinstance(json, Dict):
            for key, value in json.items():
                new_key = f"_{key}"
                if hasattr(self, new_key):
                    setattr(self, new_key, value)
                else:
                    raise AttributeError(f"attribute {new_key}")
        else:
            raise TypeError("json should be a Dict.")


class User(DataEntity):
    """User with credentials defined by an UUID."""

    filepath: str = "users.JSON"

    def __init__(
        self,
        name: str,
        password: str,
        user_uuid: Optional[str] = None,
        deleted: bool = False,
        creation_datetime: Optional[str] = None,
        update_datetime: Optional[str] = None,
    ):
        try:
            datetime_now = datetime.now(timezone.utc).strftime(DATETIME_FORMAT)
            self._user_uuid: str = (
                user_uuid if user_uuid is not None else str(uuid.uuid4())
            )
            self._name: str = name
            self._password: str = password
            self._deleted: bool = deleted if deleted is not None else False
            self._creation_datetime: str = (
                creation_datetime
                if creation_datetime is not None
                else datetime_now
            )
            self._update_datetime: str = (
                update_datetime
                if update_datetime is not None
                else datetime_now
            )
        except TypeError as te:
            raise TypeError(f"TypeError: in User __init__: {te}")
        except Exception as e:
            raise UserError(f"UserError: in User __init__: {e}")

    def get_user_name(self) -> str:
        """Gets User name."""
        return self._name

    def get_user_uuid(self) -> str:
        """Gets the User user_uuid"""
        return self._user_uuid


class Task(DataEntity):
    """Task related to a User defined by a UUID."""

    filepath: str = "tasks.JSON"

    def __init__(
        self,
        title: str,
        description: str,
        owner_uuid: str,
        task_uuid: Optional[str] = None,
        status: str = TASK_STATUSES["todo"],
        deleted: bool = False,
        creation_datetime: Optional[str] = None,
        update_datetime: Optional[str] = None,
    ):
        try:
            datetime_now = datetime.now(timezone.utc).strftime(DATETIME_FORMAT)
            self._task_uuid: str = (
                task_uuid if task_uuid is not None else str(uuid.uuid4())
            )
            self._title: str = title
            self._description: str = description
            self._status: str = (
                status if status is not None else TASK_STATUSES["todo"]
            )
            self._deleted: bool = deleted if deleted is not None else False
            self._creation_datetime: str = (
                creation_datetime
                if creation_datetime is not None
                else datetime_now
            )
            self._update_datetime: str = (
                update_datetime
                if update_datetime is not None
                else datetime_now
            )
            self._owner_uuid: str = owner_uuid
        except TypeError as te:
            raise TypeError(f"TypeError: in Type __init__: {te}")
        except Exception as e:
            raise TaskError(f"TaskError: in Type __init__: {e}")

    def __str__(self) -> str:
        return self.to_string(include_dates=True)

    def to_string(
        self,
        include_deleted: bool = False,
        include_user: bool = False,
        include_dates: bool = False,
    ) -> str:
        """Returns a string representation of the Task"""
        try:
            deleted_line = f"\n            ---- Deleted: {self._deleted} ----"
            add_deleted = (
                deleted_line
                if self._deleted is not None or self._deleted is False
                else ""
            )
            add_deleted = (
                deleted_line if include_deleted is True else add_deleted
            )

            dates_lines = f"""
            °°°° Created at: {self._creation_datetime}
            °°°° Updated at: {self._update_datetime}
            """
            add_dates = dates_lines if include_dates is True else ""

            user_line = f"\n---- User: {self._owner_uuid}"
            add_user = user_line if include_user is True else ""

            text = f"""
            ------------------------------------------------
            ------------------------------------------------
            |||| {self._title} ||||
            ---- Status: {self._status} ----
            ---- UUID: {self._task_uuid} ----{add_deleted}
            {self._description}{add_dates}{add_user}
            """
            return text
        except TypeError as te:
            raise TypeError(f"TypeError: in Type to_string: {te}")
        except Exception as e:
            raise TaskError(f"TaskError: in Type to_string: {e}")


class DataEntitySet(Set):
    """
    This set can only be of one class, related_class, it must be
    DataEntity or it's children.
    This is used to load, store and contain all the data in DataEntity objects.
    """

    related_class: Type["DataEntity"] = DataEntity

    @data_object_exception_manager
    def __init__(self, json_list: Optional[List] = None) -> None:
        if json_list is not None:
            for data_entity in json_list:
                self.add_jSON(data_entity)
        else:
            return super().__init__()

    @data_object_exception_manager
    def add(self, data_entity: DataEntity) -> None:
        """Adds DataEntity or child object into the set, verifying it."""
        if isinstance(data_entity, self.related_class):
            super().add(data_entity)
        else:
            raise TypeError(
                f"data_entity should be type {self.related_class}."
            )

    @data_object_exception_manager
    def update(self, dataEntities: Set) -> None:
        """Updates the DataEntitySet adding a Set of the related_class."""
        filtered_dataEntities = [
            data_entity
            for data_entity in dataEntities
            if isinstance(data_entity, self.related_class)
        ]
        super().update(filtered_dataEntities)

    @data_object_exception_manager
    def add_jSON(self, json: Dict) -> None:
        """
        Creates an object of the related_class type using the data \
        from the json providede and adds it to the DataEntitySet.
        """
        if isinstance(json, Dict):
            attributes = {
                attr[1:]: json.get(attr[1:], None)
                for attr in self.related_class.__dict__[
                    "__static_attributes__"
                ]
            }
            data_entity = self.related_class(**attributes)
            self.add(data_entity)
        else:
            raise TypeError("json should be type a Dict")

    @data_object_exception_manager
    def get_data_entity_by_key(
        self, key: str, value: str
    ) -> Optional[DataEntity]:
        """
        Returns an item from the DataEntitySet that has the received \
        key with the corresponding value. If it doesn't exist return None.
        """
        for data_entity in self:
            if data_entity.get_data()[key] == value:
                return data_entity
        return None

    @data_object_exception_manager
    def get_data_entity_by_uuid(self, uuid: str) -> Optional[DataEntity]:
        """Returns an item from the DataEntitySet with the received UUID."""
        class_name = self.related_class.__name__.lower()
        return self.get_data_entity_by_key(f"{class_name}_uuid", uuid)

    @data_object_exception_manager
    def get_filtered_entities(self, key_values: Dict) -> Optional[Set]:
        """
        Returns a set of related_class type that has the received \
        attributes with their corresponding values.
        """
        return {
            item
            for key in key_values.keys()
            for item in self
            if item.get_data().get(f"_{key}", None) == key_values[key]
        }

    @data_object_exception_manager
    def dump(self) -> List[Dict]:
        """
        Returns a list of dictionaries containing all the data \
        in json structure.
        """
        return [data_entity.get_data() for data_entity in self]

    def remove(self):
        raise TypeError(
            "TypeError: You can't remove by value from a DataEntitySet."
        )

    def discard(self):
        raise TypeError(
            "TypeError: You can't discard by value from a DataEntitySet."
        )

    def pop(self):
        raise TypeError(
            "TypeError: You can't pop a data entity from a DataEntitySet."
        )

    def clear(self):
        raise TypeError(
            "TypeError: You can't clear the data entity set from a \
                DataEntitySet."
        )


class UserSet(DataEntitySet):
    related_class = User

    def __init__(self, json_list: Optional[List] = None):
        super().__init__(json_list)

    def get_user_by_key(self, key: str, value: str) -> User:
        """
        Returns the User object that has the key attribute the \
        corresponding value. If it doesn't exist returns None.
        """
        try:
            return super().get_data_entity_by_key(key, value)
        except Exception as e:
            raise UserSetError(f"UserSet: in getUserByKey: {e}")

    def get_user_by_uuid(self, uuid: str) -> User:
        """
        Returns the User object that has the UUID.
        If it doesn't exist returns None.
        """
        try:
            return super().get_data_entity_by_uuid(uuid)
        except Exception as e:
            raise UserSetError(f"UserSet: in getUserByUuid: {e}")

    def get_user_by_name(self, name: str) -> User:
        """
        Returns the User object that fits the name, it should be unique.
        If it doesn't exist returns None.
        """
        try:
            return self.get_user_by_key("name", name)
        except Exception as e:
            raise UserSetError(f"UserSet: in getUserByName: {e}")

    def user_exists(self, name: str) -> bool:
        """Returns True if there's a User with the received name."""
        try:
            return True if self.get_user_by_name(name) is not None else False
        except Exception as e:
            raise UserSetError(f"UserSet: in user_exists: {e}")


class TaskSet(DataEntitySet):
    related_class = Task

    def __init__(self, json_list: Optional[List] = None):
        super().__init__(json_list)

    def get_task_by_key(self, key: str, value: str) -> Task:
        """
        Returns the Task object that has the key attribute the \
        corresponding value. If it doesn't exist returns None.
        """
        try:
            return super().get_data_entity_by_key(key, value)
        except Exception as e:
            raise TaskSetError(f"TaskSet: in getTaskByKey: {e}")

    def get_task_by_uuid(self, uuid: str) -> Task:
        """
        Returns the Task object that has UUID.
        If it doesn't exist returns None.
        """
        try:
            return super().get_data_entity_by_uuid(uuid)
        except Exception as e:
            raise TaskSetError(f"TaskSet: in getTaskByUuid: {e}")

    def get_user_tasks(
        self,
        owner_uuid: str,
        filter_status: Optional[str] = None,
        inclue_delete: bool = False,
    ) -> Set:
        """
        Returns a set of Task objects related to a User, it can be filtered by
        deleted and status values.
        """
        try:
            filter_data: Dict[Optional[str], Any] = {"owner_uuid": owner_uuid}
            filter_data["status"] = (
                filter_status if filter_status is not None else None
            )
            filter_data["deleted"] = False if inclue_delete else None
            return super().get_filtered_entities(filter_data)
        except Exception as e:
            raise TaskSetError(f"TaskSet: in getUserTasks: {e}")

    def get_last_user_created_task(self) -> Task:
        """Returns the most recently created Task."""
        try:
            return max(
                self, key=lambda task: task.get_data()["creation_datetime"]
            )
        except Exception as e:
            raise TaskSetError(f"TaskSet: in getLastUserCreatedTask: {e}")

    def delete_task(self, uuid_text: str) -> None:
        """Searches for the Task with the UUID and excutes a soft-delete."""
        try:
            task = self.get_task_by_uuid(uuid_text)
            datetime_now = datetime.now(timezone.utc).strftime(DATETIME_FORMAT)
            task.udpate({"deleted": True, "update_datetime": datetime_now})
        except Exception as e:
            raise TaskSetError(f"TaskSet: in deleteTask: {e}")

    def update_task(
        self, uuid_text: str, title: str, description: str, status: str
    ) -> None:
        """Searches for the Task with the UUID and updateds tje information."""
        try:
            task = self.get_task_by_uuid(uuid_text)
            task_data = task.get_data()

            datetime_now = datetime.now(timezone.utc).strftime(DATETIME_FORMAT)
            new_title = title if title is not None else task_data["_title"]
            new_description = (
                description
                if description is not None
                else task_data["_description"]
            )
            new_status = status if status is not None else task_data["_status"]

            task.udpate(
                {
                    "title": new_title,
                    "description": new_description,
                    "update_datetime": datetime_now,
                    "status": new_status,
                }
            )
        except Exception as e:
            raise TaskSetError(f"TaskSet: in deleteTask: {e}")
