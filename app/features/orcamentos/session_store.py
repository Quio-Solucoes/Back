from __future__ import annotations

from typing import Optional

from app.domain.models import Conversa

_sessoes: dict[str, Conversa] = {}


def get_or_create_sessao(session_id: str) -> Conversa:
    return _sessoes.setdefault(session_id, Conversa())


def get_sessao(session_id: str) -> Optional[Conversa]:
    return _sessoes.get(session_id)


def reset_sessao(session_id: str) -> bool:
    if session_id not in _sessoes:
        return False
    del _sessoes[session_id]
    return True

