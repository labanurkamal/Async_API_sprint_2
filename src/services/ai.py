import os
import logging
import spacy
from fastapi import Depends

INTENT_MODEL_PATH = "/opt/app/src/output/intent/output_intent/model-best"
NER_MODEL_PATH = "/opt/app/src/output/ner/model-best"


class IntentNERModel:

    def model_path_exists(self, model_path: str) -> None:
        try:
            if not os.path.exists(model_path):
                raise FileNotFoundError
        except FileNotFoundError:
            logging.error(f"Model path {model_path} not found.")

    def load_model(self, model_path: str):
        self.model_path_exists(model_path)
        return spacy.load(model_path)

    def model_intent(self, text):
        nlp = self.load_model(INTENT_MODEL_PATH)
        doc = nlp(text)

        scores = {k: v for k, v in doc.cats.items()}
        predicted_category = max(scores.items(), key=lambda x: x[1])
        print(f"Текст: {text}")
        print(f"Распознанная категория: {predicted_category[0]}")

        return predicted_category[0]

    def model_entities(self, text):
        nlp = self.load_model(NER_MODEL_PATH)

        doc = nlp(text)
        entities = {ent.text: ent.label_ for ent in doc.ents}
        print(f"Текст: {text}")
        print(f"Распознанные сущности: {entities}")
        return entities


class AIService:
    def __init__(self, intent_ner_model: IntentNERModel):
        self.intent_ner_model = intent_ner_model

    def extract_entities(self, text: str):
        return self.intent_ner_model.model_entities(text)

    def define_intent(self, text: str):
        return self.intent_ner_model.model_intent(text)

    def process_request(self, text: str):
        entities = self.extract_entities(text)
        intent = self.define_intent(text)

        return self.handle_request(entities, intent)

    def handle_request(self, entities, intent):

        if not intent:
            return "Не удалось определить намерение."

        INTENT_HANDLERS = {
            "film_description": ("FILM", "Описание фильма {name}: ..."),
            "film_rating": ("FILM", "Рейтинг фильма {name}: 8.5/10"),
            "actor_info": ("PERSON", "Информация актера {name}: ..."),
            "director_info": ("PERSON", "Информация режиссёра {name}: ..."),
            "writer_info": ("PERSON", "Информация сценари́ста {name}: ..."),
            "actor_movies": ("PERSON", "Вот фильмы, в которых снимался {name}: ..."),
            "director_movies": ("PERSON", "Вот фильмы, снятые {name}: ..."),
        }

        if intent not in INTENT_HANDLERS:
            return "Я пока не умею отвечать на такие вопросы."

        entity_type, response_template = INTENT_HANDLERS[intent]
        entity_name = self.get_entity_by_type(entities, entity_type)

        return response_template.format(name=entity_name) if entity_name else f"Не найдено {entity_type.lower()} в запросе."

    @staticmethod
    def get_entity_by_type(entities, entity_type):
        return next((name for name, type_ in entities.items() if type_==entity_type), None)

def get_ai_service() -> AIService:
    intent_ner_model: IntentNERModel = IntentNERModel()
    return AIService(intent_ner_model=intent_ner_model)

