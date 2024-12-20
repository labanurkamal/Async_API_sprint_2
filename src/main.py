from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from api.v1 import films, genres, persons
from core.config import settings
from dependencies.container import CoreContainer, ServiceContainer


@asynccontextmanager
async def lifespan(app: FastAPI):

    core_container = CoreContainer()
    service_container = ServiceContainer()

    app.core_container = core_container
    app.service_container = service_container

    service_container.wire(
        modules=[
            "api.v1.films",
            "api.v1.genres",
            "api.v1.persons",
        ]
    )
    try:
        yield
    finally:
        await core_container.redis_client().close()
        await core_container.elastic_client().close()


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
