from functools import lru_cache

from elasticsearch import AsyncElasticsearch
from fastapi import Depends
from redis.asyncio import Redis

from .repositories.repo import RedisCache, ElasticStorage
from db.elastic import get_elastic
from db.redis import get_redis
from models.models import Film
from services.services import BaseService


class FilmService(BaseService[Film]):
    def __init__(self, redis: RedisCache, elastic: ElasticStorage):
        super().__init__(redis, elastic)
        self._index = "movies"
        self._model = Film


@lru_cache()
def get_film_service(
    redis: Redis = Depends(get_redis),
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> FilmService:
    return FilmService(RedisCache(redis), ElasticStorage(elastic))
