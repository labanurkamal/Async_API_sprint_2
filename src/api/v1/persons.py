from http import HTTPStatus
from typing import Optional

from fastapi import APIRouter, Depends, Query

from . import validators
from .models import PersonFilm, ShortFilm
from services.person import PersonServices, get_person_service

router = APIRouter()


@router.get(
    "/search/",
    summary="Поиск по персонажам",
    description="Ищет персонажей по имени. Возвращает список персонажей с их фильмами.",
    response_model=list[PersonFilm],
)
async def get_person_search(
    person_service: PersonServices = Depends(get_person_service),
    query: Optional[str] = Query(None, description="Имя персонажа для поиска."),
    page_number: Optional[int] = Query(
        1, ge=1, description="Номер страницы для пагинации."
    ),
    page_size: Optional[int] = Query(
        50, ge=1, description="Количество результатов на странице."
    ),
) -> list[PersonFilm]:
    search_query = {
        "query": {
            "multi_match": {
                "query": query,
                "fields": [
                    "full_name",
                ],
            }
        },
        "from": page_size * (page_number - 1),
        "size": page_size,
    }
    person_search = await person_service.get_by_search(search_query)
    validators.http_exception(
        person_search, HTTPStatus.NOT_FOUND, "Персонажи не найдены."
    )

    return person_search


@router.get(
    "/{person_id}/",
    summary="Получение информации о персонаже",
    description="Возвращает полную информацию о персонаже по его идентификатору.",
    response_model=PersonFilm,
)
async def get_person_details(
    person_id: str, person_service: PersonServices = Depends(get_person_service)
) -> PersonFilm:
    person = await person_service.get_by_id(person_id)
    validators.http_exception(person, HTTPStatus.NOT_FOUND, "Персонаж не найден.")

    return person


@router.get(
    "/{person_id}/film/",
    summary="Получение фильмов персонажа",
    description="Возвращает список фильмов, в которых снялся персонаж по его идентификатору.",
    response_model=list[ShortFilm],
)
async def get_person_film(
    person_id: str, person_service: PersonServices = Depends(get_person_service)
) -> list[ShortFilm]:
    person_films = await get_person_details(person_id, person_service)
    validators.http_exception(
        person_films, HTTPStatus.NOT_FOUND, "Фильмов персонажа не найден."
    )
    return person_films.films
