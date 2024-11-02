from functools import lru_cache

from elasticsearch import AsyncElasticsearch
from fastapi import Depends
from redis.asyncio import Redis

from .repositories.repo import RedisCache, ElasticStorage
from db.elastic import get_elastic
from db.redis import get_redis
from models.models import PersonFilm
from services.services import BaseService


class PersonServices(BaseService[PersonFilm]):
    def __init__(self, redis: RedisCache, elastic: ElasticStorage):
        super().__init__(redis, elastic)
        self._index = "persons"
        self._model = PersonFilm


@lru_cache()
def get_person_service(
    redis: Redis = Depends(get_redis),
    elastic: AsyncElasticsearch = Depends(get_elastic),
):
    return PersonServices(RedisCache(redis), ElasticStorage(elastic))
