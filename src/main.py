from contextlib import asynccontextmanager

from elasticsearch import AsyncElasticsearch
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from redis.asyncio import Redis

from api.v1 import films, genres, persons
from core.config import settings
from db import elastic, redis


@asynccontextmanager
async def lifespan(app: FastAPI):
    redis.redis = Redis(
        host=settings.redis_host,
        port=settings.redis_port,
        password=settings.redis_password,
    )
    elastic.es = AsyncElasticsearch(hosts=[settings.elastic_url])

    try:
        yield
    finally:
        await redis.redis.close()
        await elastic.es.close()


app = FastAPI(
    lifespan=lifespan,
    title=settings.project_name,
    docs_url="/api/openapi",
    openapi_url="/api/openapi.json",
    default_response_class=ORJSONResponse,
)

app.include_router(films.router, prefix="/api/v1/films", tags=["FILMS"])
app.include_router(genres.router, prefix="/api/v1/genres", tags=["GENRES"])
app.include_router(persons.router, prefix="/api/v1/persons", tags=["PERSONS"])
