from typing import Optional

from app.features.chat.conversations.model import Conversa


conversas: dict[str, Conversa] = {}

def get_or_create_conversa(session_id: str) -> Conversa:
    return conversas.setdefault(session_id, Conversa())

def get_conversa(session_id: str) -> Optional[Conversa]:
    return conversas.get(session_id)

def resetar_conversa(session_id: str) -> dict:
    """Reseta e responde em uma única função."""
    if session_id not in conversas:
        return {"response": "Conversa nao encontrada."}
    del conversas[session_id]
    return {"response": "Conversa resetada com sucesso!"}
