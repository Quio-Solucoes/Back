from fastapi import APIRouter

from app.features.conversations.service import resetar_conversa

router = APIRouter(prefix="/conversations", tags=["conversations"])


@router.post("/reset/{session_id}")
def reset_conversation(session_id: str) -> dict:
    return resetar_conversa(session_id)
