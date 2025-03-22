import logging
from typing import Dict, Any
from dependency_injector.wiring import Provide, inject
from dependencies.container import ServiceContainer

from fastapi import APIRouter, Request, Depends
from pydantic import BaseModel

# from services.ai import AIService
router = APIRouter()

class YandexVoiceRequest(BaseModel):
    meta: Dict[str, Any]
    session: Dict[str, Any]
    request: Dict[str, Any]
    version: str

@router.post("/yandex")
@inject
async def voice(
    request: YandexVoiceRequest,
    ai_service = Depends(Provide[ServiceContainer.ai_service]),
):
    text = request.request.get("original_utterance", "")

    response = await ai_service.process_request(text)

    return {
        "version": request.version,
        "session": request.session,
        "response": {
            "text": response,
            "end_session": False
        }
    }
