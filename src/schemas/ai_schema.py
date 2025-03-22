from enum import Enum


class IntentFields(str, Enum):
    film_description = 'description'
    film_rating = 'imdb_rating'
    actor_info = 'actors'
    director_info = 'directors'
    writer_info = 'writers'
    actor_movies = 'films'
    director_movies = 'films'


class EntityType(str, Enum):
    GENRE = 'GENRE'
    PERSON = 'PERSON'
    FILM = 'FILM'
