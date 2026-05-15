from fastapi import APIRouter

from app.features.chat.voz.schemas import ChatVoiceRequest
from app.features.chat.voz.service import processar_mensagem_voz


router = APIRouter(tags=["chat-voz"])


@router.post("/chat-voz")
def chat_voz(payload: ChatVoiceRequest) -> dict:
    return processar_mensagem_voz(payload)
