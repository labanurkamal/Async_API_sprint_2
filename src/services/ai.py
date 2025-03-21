import os
import logging
import spacy


INTENT_MODEL_PATH = "/opt/app/src/output/intent/output_intent/model-best"
NER_MODEL_PATH = "/opt/app/src/output/ner/model-best"


class IntentNerClass:

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

    def model_ner(self, text):
        nlp = self.load_model(NER_MODEL_PATH)

        doc = nlp(text)
        entities = {ent.text: ent.label_ for ent in doc.ents}
        print(f"Текст: {text}")
        print(f"Распознанные сущности: {entities}")



def get_intent_ner_class() -> IntentNerClass:
    return IntentNerClass()

