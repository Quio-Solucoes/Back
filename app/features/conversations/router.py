from fastapi import APIRouter

from app.features.chat.service import conversas

router = APIRouter()


@router.post("/reset/{session_id}")
def reset_conversa(session_id: str):
    if session_id in conversas:
        del conversas[session_id]
        return {"response": "? Conversa resetada com sucesso!"}
    return {"response": "?? Conversa não encontrada."}

