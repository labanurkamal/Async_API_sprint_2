import hashlib
import json
import logging
from typing import Any, Type, Optional, TypeVar

from pydantic import BaseModel

from .repositories.interfaces import BaseInterface
from .repositories.repo import RedisCache, ElasticStorage


FILM_CACHE_EXPIRE_IN_SECONDS = 60 * 3

T = TypeVar("T", bound=BaseModel)


class BaseService(BaseInterface[T]):

    def __init__(self, redis: RedisCache, elastic: ElasticStorage) -> None:
        self.redis = redis
        self.elastic = elastic
        self._index: Optional[str] = None
        self._model: Optional[Type[T]] = None

    async def get_by_id(self, obj_id: str) -> Optional[T]:
        cache_key = self._get_cache_key(obj_id)
        cached_data = await self.redis.get(name=cache_key)

        if cached_data:
            logging.info("ANSWER FROM REDIS")
            return self._model.model_validate(cached_data)

        storage_data = await self.elastic.get(index=self._index, id=obj_id)
        if not storage_data:
            return None

        model_instance = self._model(**storage_data)
        logging.info("ANSWER FROM ELASTIC")
        await self.redis.set(
            name=cache_key,
            value=model_instance.model_dump_json(),
            ex=FILM_CACHE_EXPIRE_IN_SECONDS,
        )

        return model_instance

    async def get_by_search(self, body: dict[str, Any] = {}) -> Optional[list[T]]:
        cache_key = self._get_cache_key_for_query(body)
        cached_data = await self.redis.get(name=cache_key)

        if cached_data:
            logging.info("ANSWER FROM REDIS")
            return [self._model.model_validate(data) for data in cached_data]

        storage_data = await self.elastic.search(index=self._index, body=body)
        if not storage_data:
            return None

        model_instance = [self._model(**doc["_source"]) for doc in storage_data]
        logging.info("ANSWER FROM ELASTIC")
        await self.redis.set(
            name=cache_key,
            value=json.dumps([model.model_dump() for model in model_instance]),
            ex=FILM_CACHE_EXPIRE_IN_SECONDS,
        )

        return model_instance

    def _get_cache_key_for_query(self, body: dict[str, Any]) -> str:
        query_string = json.dumps(body, sort_keys=True)
        query_hash = hashlib.md5(query_string.encode()).hexdigest()

        return f"{self._index}:query:{query_hash}"

    def _get_cache_key(self, obj_id: str) -> str:
        return f"{self._index}:{obj_id}"
