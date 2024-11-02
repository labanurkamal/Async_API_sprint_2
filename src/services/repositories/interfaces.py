from abc import ABC, abstractmethod
from typing import Optional, Any, Union, TypeVar, Generic

T = TypeVar("T")



class CacheInterface(ABC):

    @abstractmethod
    async def get(self, **kwargs: Any) -> Union[dict[str, Any], None]:
        pass


    @abstractmethod
    async def set(self, **kwargs: Any) -> None:
        pass



class StorageInterface(ABC):

    @abstractmethod
    async def get(self, **kwargs: Any) -> Union[dict[str, Any], None]:
        pass

    @abstractmethod
    async def search(self, **kwargs: Any) -> Union[list[dict[str, Any]], None]:
        pass


class BaseInterface(ABC, Generic[T]):

    @abstractmethod
    async def get_by_id(self, obj_id: str) -> Optional[T]:
        pass

    @abstractmethod
    async def get_by_search(self, body: dict[str, Any]) -> Optional[list[T]]:
        pass