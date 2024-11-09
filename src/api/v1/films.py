from http import HTTPStatus
from typing import Optional, Literal

from fastapi import APIRouter, Depends, Query

from . import validators
from .models import ShortFilm
from models.models import Film
from services.film import FilmService, get_film_service

router = APIRouter()


@router.get(
    "/",
    summary="Получить популярные фильмы или фильмы по жанру",
    description="Этот эндпоинт возвращает список популярных фильмов или фильмов, отфильтрованных по жанру.",
    responses={
        HTTPStatus.OK.value: {"description": "Список фильмов успешно получен"},
        HTTPStatus.NOT_FOUND.value: {"description": "Фильмы не найдены"},
    },
    response_model=list[ShortFilm],
)
async def get_popular_or_by_genre_films(
    film_service: FilmService = Depends(get_film_service),
    genre: Optional[str] = Query(None, description="ID жанра для фильтрации фильмов"),
    sort: Optional[Literal["-imdb_rating", "imdb_rating"]] = Query(
        "-imdb_rating",
        description="Поле для сортировки фильмов. Используйте '-' для обратного порядка.",
    ),
    page_size: Optional[int] = Query(
        50, ge=1, description="Количество фильмов на странице"
    ),
    page_number: Optional[int] = Query(1, ge=1, description="Номер страницы"),
) -> list[ShortFilm]:
    query = {
        "query": {
            "nested": {
                "path": "genre",
                "query": {
                    "bool": {"must": [{"term": {"genre.id": genre}}] if genre else []}
                },
            }
        },
        "sort": [
            {sort.lstrip("-"): {"order": "desc" if sort.startswith("-") else "asc"}}
        ],
        "from": page_size * (page_number - 1),
        "size": page_size,
    }
    list_film = await film_service.get_by_search(query)
    validators.http_exception(list_film, HTTPStatus.NOT_FOUND, "Фильмы не найдены")

    return list_film


@router.get(
    "/search/",
    summary="Поиск фильмов",
    description="Этот эндпоинт позволяет искать фильмы по названию или описанию.",
    responses={
        HTTPStatus.OK.value: {"description": "Фильмы найдены по запросу"},
        HTTPStatus.NOT_FOUND.value: {"description": "Фильмы по запросу не найдены"},
    },
    response_model=list[ShortFilm],
)
async def get_film_search(
    film_service: FilmService = Depends(get_film_service),
    query: str = Query(..., description="Поисковый запрос для фильмов"),
    page_size: Optional[int] = Query(
        50, ge=1, description="Количество фильмов на странице"
    ),
    page_number: Optional[int] = Query(1, ge=1, description="Номер страницы"),
) -> list[ShortFilm]:
    search_query = {
        "query": {"multi_match": {"query": query, "fields": ["title", "description"]}},
        "from": page_size * (page_number - 1),
        "size": page_size,
    }

    film = await film_service.get_by_search(search_query)
    validators.http_exception(
        film, HTTPStatus.NOT_FOUND, "Фильмы по запросу не найдены."
    )
    return film


@router.get(
    "/{film_id}/",
    summary="Получить детали фильма",
    description="Этот эндпоинт возвращает информацию о фильме по его ID.",
    responses={
        HTTPStatus.OK.value: {"description": "Информация о фильме найдена"},
        HTTPStatus.NOT_FOUND.value: {"description": "Фильм не найден"},
    },
    response_model=Film,
)
async def get_film_details(
    film_id: str, film_service: FilmService = Depends(get_film_service)
) -> Film:
    film = await film_service.get_by_id(film_id)
    validators.http_exception(film, HTTPStatus.NOT_FOUND, "Фильм не найден.")

    return film
