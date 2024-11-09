import json
from typing import Any, Union

from elasticsearch import AsyncElasticsearch, NotFoundError
from redis.asyncio import Redis

from .interfaces import CacheInterface, StorageInterface


class RedisCache(CacheInterface):
    def __init__(self, redis: Redis) -> None:
        self.redis = redis

    async def get(self, **kwargs: Any) -> Union[dict[str, Any], None]:
        cached_data = await self.redis.get(**kwargs)
        if not cached_data:
            return None

        return json.loads(cached_data)

    async def set(self, **kwargs: Any) -> None:
        await self.redis.set(**kwargs)


class ElasticStorage(StorageInterface):
    def __init__(self, elastic: AsyncElasticsearch) -> None:
        self.elastic = elastic

    async def get(self, **kwargs: Any) -> Union[dict[str, Any], None]:
        try:
            doc = await self.elastic.get(**kwargs)
        except NotFoundError:
            return None

        return doc["_source"]

    async def search(self, **kwargs: Any) -> Union[list[dict[str, Any]], None]:
        try:
            docs = await self.elastic.search(**kwargs)
        except NotFoundError:
            return None

        return docs["hits"]["hits"]
