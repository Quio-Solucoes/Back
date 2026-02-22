from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.features.chat.service import processar_mensagem
from app.features.chat.voz.dtos import ChatVoiceRequest


def processar_mensagem_voz(payload: ChatVoiceRequest, db: Session | None = None) -> dict:
    message = str(payload.message or "").strip()
    session_id = payload.session_id or "default"

    if not message:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Audio invalido",
        )

    return processar_mensagem(message=message, session_id=session_id, db=db)
