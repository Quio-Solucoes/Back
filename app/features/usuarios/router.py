from fastapi import APIRouter

from app.features.usuarios.schemas import CreateUsuarioRequest, UsuarioResponse
from app.features.usuarios.service import criar_usuario

router = APIRouter(prefix="/usuarios", tags=["usuarios"])


@router.post("", response_model=UsuarioResponse)
def post_criar_usuario(payload: CreateUsuarioRequest) -> UsuarioResponse:
    return criar_usuario(payload)

