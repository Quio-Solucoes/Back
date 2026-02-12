from typing import Optional

from app.domain.models import Conversa

conversas: dict[str, Conversa] = {}


def get_or_create_conversa(session_id: str) -> Conversa:
    return conversas.setdefault(session_id, Conversa())


def get_conversa(session_id: str) -> Optional[Conversa]:
    return conversas.get(session_id)


def reset_conversa(session_id: str) -> bool:
    if session_id not in conversas:
        return False
    del conversas[session_id]
    return True
