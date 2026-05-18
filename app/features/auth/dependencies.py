from __future__ import annotations

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.config.settings import SECRET_KEY
from app.domain.models import Usuario
from app.features.auth.security import decode_access_token
from app.features.usuarios.store import get_user_by_id

_bearer = HTTPBearer(auto_error=False)


def get_current_user(credentials: HTTPAuthorizationCredentials | None = Depends(_bearer)) -> Usuario:
    if not credentials or credentials.scheme.lower() != "bearer":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Nao autenticado")

    try:
        payload = decode_access_token(credentials.credentials, secret_key=SECRET_KEY)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc

    user = get_user_by_id(payload.sub)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Nao autenticado")

    return user


def _authorize(user: Usuario, required: str) -> None:
    """
    Centraliza regras de autorização/permissões.

    Hoje: somente verifica autenticação (o `user` já vem autenticado).
    Amanhã: validar roles/ACL/plano com base em `required`.
    """

    _ = user
    _ = required


def require_permission(user: Usuario = Depends(get_current_user)) -> Usuario:
    """
    Ponto único para controlar permissões básicas.

    Se você decidir adicionar roles/perfis depois, a regra vai aqui,
    sem precisar mexer em todas as rotas.
    """

    _authorize(user, "basic")
    return user

