from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.config.settings import SECRET_KEY
from app.features.auth.schemas import LoginRequest, TokenResponse
from app.features.auth.security import decode_access_token
from app.features.auth.service import login
from app.features.usuarios.schemas import UsuarioResponse
from app.features.usuarios.store import get_user_by_id

router = APIRouter(prefix="/auth", tags=["auth"])
_bearer = HTTPBearer(auto_error=False)


@router.post("/login", response_model=TokenResponse)
def post_login(payload: LoginRequest) -> TokenResponse:
    return login(payload)


@router.get("/me", response_model=UsuarioResponse)
def get_me(credentials: HTTPAuthorizationCredentials | None = Depends(_bearer)) -> UsuarioResponse:
    if not credentials or credentials.scheme.lower() != "bearer":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Nao autenticado")

    try:
        payload = decode_access_token(credentials.credentials, secret_key=SECRET_KEY)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc

    user = get_user_by_id(payload.sub)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Nao autenticado")

    return UsuarioResponse(
        id=user.id,
        nome=user.nome,
        email=user.email,
        telefone=user.telefone,
        criado_em=user.criado_em,
    )
