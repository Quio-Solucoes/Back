from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.db import get_db
from app.features.chat.voz.dtos import ChatVoiceRequest
from app.features.chat.voz.service import processar_mensagem_voz


router = APIRouter(tags=["chat-voz"])


@router.post("/chat-voz")
def chat_voz(payload: ChatVoiceRequest, db: Session = Depends(get_db)) -> dict:
    return processar_mensagem_voz(payload, db=db)
