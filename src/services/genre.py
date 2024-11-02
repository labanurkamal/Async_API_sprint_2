from functools import lru_cache

from elasticsearch import AsyncElasticsearch
from fastapi import Depends
from redis.asyncio import Redis

from .repositories.repo import RedisCache, ElasticStorage
from db.elastic import get_elastic
from db.redis import get_redis
from models.models import Genre
from services.services import BaseService


class GenreService(BaseService[Genre]):
    def __init__(self, redis: RedisCache, elastic: ElasticStorage) -> None:
        super().__init__(redis, elastic)
        self._index = "genres"
        self._model = Genre


@lru_cache()
def get_genre_service(
    redis: Redis = Depends(get_redis),
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> GenreService:
    return GenreService(RedisCache(redis), ElasticStorage(elastic))
