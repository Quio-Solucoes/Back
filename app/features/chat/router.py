from fastapi import APIRouter, HTTPException

from app.features.chat.schemas import ChatRequest
from app.features.chat.service import processar_mensagem

router = APIRouter(tags=["chat"])


@router.options("/chat")
def chat_options() -> dict:
    return {"status": "ok"}


@router.post("/chat")
def chat(payload: ChatRequest) -> dict:
    try:
        message = str(payload.message or "").strip()
        session_id = payload.session_id or "default"
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Erro ao processar requisicao: {exc}") from exc

    return processar_mensagem(message=message, session_id=session_id)
