import logging
from typing import Dict, Any

from fastapi import APIRouter, Request, Depends
from pydantic import BaseModel

from services.ai import AIService, get_ai_service
router = APIRouter()

class YandexVoiceRequest(BaseModel):
    meta: Dict[str, Any]
    session: Dict[str, Any]
    request: Dict[str, Any]
    version: str

@router.post("/yandex")
async def voice(
    request: YandexVoiceRequest,
    ai_service: AIService = Depends(get_ai_service)
):
    text = request.request.get("original_utterance", "")

    response = ai_service.process_request(text)

    return {
        "version": request.version,
        "session": request.session,
        "response": {
            "text": response,
            "end_session": False
        }
    }
