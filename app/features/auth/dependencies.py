from collections.abc import Callable
from typing import Any

from fastapi import Depends, Header, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from app.features.empresas.memberships.enums import MembershipRole, MembershipStatus
from app.features.empresas.memberships.schema import Membership
from sqlalchemy.orm import Session

from app.config.settings import INTERNAL_API_KEY
from app.db.db import get_db
from app.features.auth.config import JWT_ALG, JWT_SECRET
from app.features.users.schema import User


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def decode_access_token(token: str) -> dict[str, Any]:
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALG])
    except JWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalido ou expirado",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    payload = decode_access_token(token)
    user_id = payload.get("user_id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token sem usuario",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = db.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario do token nao encontrado",
            headers={"WWW-Authenticate": "Bearer"},
        )

    membership_id = payload.get("membership_id")
    if membership_id:
        membership = db.get(Membership, membership_id)
        if not membership or membership.status != MembershipStatus.ACTIVE:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Membership inativa ou nao encontrada",
            )
        user.current_membership = membership  # type: ignore[attr-defined]

    user.token_claims = payload  # type: ignore[attr-defined]
    return user


def require_roles(*roles: MembershipRole) -> Callable[[User], User]:
    role_values = {r.value for r in roles}

    def dependency(user: User = Depends(get_current_user)) -> User:
        claims = getattr(user, "token_claims", {})
        token_role = claims.get("role")
        if token_role not in role_values:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Sem permissao para esta acao",
            )
        return user

    return dependency


def require_internal_api_key(x_internal_key: str = Header(default="")) -> None:
    if not INTERNAL_API_KEY or x_internal_key != INTERNAL_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Chave interna invalida",
        )
