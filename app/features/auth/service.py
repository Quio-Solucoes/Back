from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.features.auth.schemas import LoginRequest, TokenResponse
from app.features.auth.security import create_access_token, verify_password
from app.features.empresas.enums import EmpresaStatus
from app.features.users.enums import UserStatus
from app.features.users.service import find_user_by_email, set_last_login_now


def login(db: Session, payload: LoginRequest) -> TokenResponse:
    user = find_user_by_email(db=db, normalized_email=payload.email)

    invalid_credentials = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciais invalidas",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if not user or not verify_password(payload.password, user.password_hash):
        raise invalid_credentials

    if user.status != UserStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario inativo ou suspenso",
        )

    if not user.empresa or user.empresa.status != EmpresaStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Empresa inativa, suspensa ou cancelada",
        )

    set_last_login_now(db=db, user=user)

    token = create_access_token(
        {
            "sub": user.id,
            "empresa_id": user.empresa_id,
            "tenant_id": user.empresa_id,
            "role": user.role.value,
        }
    )
    return TokenResponse(access_token=token)
