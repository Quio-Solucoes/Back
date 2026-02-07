from __future__ import annotations

from typing import Optional

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from app.features.chat.service import processar_mensagem

router = APIRouter()


class ChatRequest(BaseModel):
    message: Optional[str] = None
    session_id: Optional[str] = "default"


@router.post("/chat")
def chat(payload: ChatRequest):
    data, status_code = processar_mensagem(
        message=str(payload.message or "").strip(),
        session_id=payload.session_id or "default",
    )
    return JSONResponse(content=data, status_code=status_code)

