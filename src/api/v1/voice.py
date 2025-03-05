import logging
from typing import Dict, Any

from fastapi import APIRouter, Request
from pydantic import BaseModel

router = APIRouter()

class YandexVoiceRequest(BaseModel):
    meta: Dict[str, Any]
    session: Dict[str, Any]
    request: Dict[str, Any]
    version: str

@router.post("/yandex")
async def voice(request: YandexVoiceRequest):
    response_text = "Привет! Это тестовый ответ от сервера."

    logging.info(request)
    return {
        "version": request.version,
        "session": request.session,
        "response": {
            "text": response_text,
            "end_session": False
        }
    }