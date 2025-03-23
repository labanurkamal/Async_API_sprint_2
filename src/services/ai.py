import os
import logging
import spacy
from fastapi import Depends
from .services import BaseInterface
from .film import FilmService
from .person import PersonService
from schemas.ai_schema import IntentFields, EntityType

INTENT_MODEL_PATH = "/opt/app/src/output/intent/output_intent/model-best"
NER_MODEL_PATH = "/opt/app/src/output/ner/model-best"


class IntentNERModel:
    def __init__(self):
        self.intent_nlp = spacy.load(INTENT_MODEL_PATH)
        self.ner_nlp = spacy.load(NER_MODEL_PATH)

    def model_intent(self, text):
        doc = self.intent_nlp(text)

        scores = {k: v for k, v in doc.cats.items()}
        predicted_category = max(scores.items(), key=lambda x: x[1])[0]

        return predicted_category

    def model_entities(self, text):
        doc = self.ner_nlp(text)
        entities = {ent.text: ent.label_ for ent in doc.ents}

        return entities


class AIService:
    def __init__(
        self,
        film_service,
        person_service,
        intent_ner_model,
    ):
        self.film_service = film_service
        self.person_service = person_service
        self.intent_ner_model = intent_ner_model

    async def handle_request(self, entities, intent):

        if not intent:
            return "Не удалось определить намерение."

        INTENT_HANDLERS = {
            "film_description": "Описание фильма {name}: ...",
            "film_rating": "Рейтинг фильма {name}:",
            "actor_info": "Информация актера {name}: ...",
            "director_info": "Информация режиссёра {name}: ...",
            "writer_info": "Информация сценари́ста {name}: ...",
            "actor_movies": "Вот фильмы, в которых снимался {name}: ...",
            "director_movies": "Вот фильмы, снятые {name}: ...",
        }

        if intent not in INTENT_HANDLERS:
            return "Я пока не умею отвечать на такие вопросы."

        if entities:
            entity_name, entity_type = next(iter(entities.items()))
        else:
            entity_name, entity_type = None, None

        es_query = await self.es_query(query=entity_name, entity_type=entity_type)
        logging.info(f'Запрос для Elasticsearch: {es_query}')

        response_template = INTENT_HANDLERS[intent]
        intent_field = IntentFields[intent].value

        result = await self.get_result(entity_type, es_query, intent_field)

        return response_template.format(name=result)

    async def get_result(self, entity_type, es_query, intent_field):
        service = await self.define_service(entity_type)
        search = await service.get_by_search(es_query)

        if not search:
            return "Данные не найдены."

        results = []
        for item in search:
            value = getattr(item, intent_field, "Нет данных")
            logging.info(f"VALUE: {value}")

            if isinstance(value, list) and value:
                # Определяем нужное поле динамически
                attr = "title" if hasattr(value[0], "title") else "full_name" if hasattr(value[0], "full_name") else None
                if attr:
                    value = ", ".join([getattr(v, attr, str(v)) for v in value])
                else:
                    value = ", ".join([str(v) for v in value])  # На случай других списков

                logging.info(f"VALUE LIST: {value}")

            results.append(str(value))

        return ", ".join(results)

    async def define_service(self, entity_type) -> BaseInterface:
        if entity_type == EntityType.PERSON:
            return self.person_service
        elif entity_type == EntityType.FILM:
            return self.film_service
        else:
            raise ValueError(f"Неизвестный тип сущности: {entity_type}")

    @staticmethod
    async def es_query(query, entity_type):
        if entity_type == EntityType.PERSON:
            fields = 'full_name'
        elif entity_type == EntityType.FILM:
            fields = 'title'
        else:
            fields = None
        return {"query": {"multi_match": {"query": query, "fields": [fields]}}}

    async def process_request(self, text: str):
        entities = self.intent_ner_model.model_entities(text)
        intent = self.intent_ner_model.model_intent(text)

        log_e = tuple(*entities.items())
        logging.info(f'1. Сущность: {entities}, Намериние: {intent}')
        logging.info(f'2. Имя: {log_e[0]}. Относиться: {log_e[1]}. Что нужно от {log_e[1]} нужно {intent}')
        return await self.handle_request(entities, intent)
