from fastapi import HTTPException, status

from app.config.settings import ACCESS_TOKEN_EXPIRE_SECONDS, SECRET_KEY
from app.features.auth.schemas import LoginRequest, TokenResponse
from app.features.auth.security import create_access_token, hash_password, needs_rehash, verify_password
from app.features.usuarios.store import get_user_by_email


def login(payload: LoginRequest) -> TokenResponse:
    user = get_user_by_email(payload.email)
    if not user or not verify_password(payload.senha, user.senha_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciais invalidas")

    if needs_rehash(user.senha_hash):
        try:
            user.senha_hash = hash_password(payload.senha)
        except Exception:
            pass

    token = create_access_token(
        user.id,
        secret_key=SECRET_KEY,
        expires_in_seconds=ACCESS_TOKEN_EXPIRE_SECONDS,
    )
    return TokenResponse(access_token=token, expires_in=ACCESS_TOKEN_EXPIRE_SECONDS)
