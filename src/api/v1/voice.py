import logging
from typing import Dict, Any

from fastapi import APIRouter, Request, Depends
from pydantic import BaseModel

from services.ai import get_intent_ner_class, IntentNerClass
router = APIRouter()

class YandexVoiceRequest(BaseModel):
    meta: Dict[str, Any]
    session: Dict[str, Any]
    request: Dict[str, Any]
    version: str

@router.post("/yandex")
async def voice(
    request: YandexVoiceRequest,
    ai_class: IntentNerClass = Depends(get_intent_ner_class)
):
    response_text = "Привет! Это тестовый ответ от сервера."

    text = request["request"]["original_utterance"]
    intent = ai_class.model_intent(text)
    request["request"]["nlu"]["intents"] = intent
    logging.info(request)
    return {
        "version": request.version,
        "session": request.session,
        "response": {
            "text": response_text,
            "end_session": False
        }
    }