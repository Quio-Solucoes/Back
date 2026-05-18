from fastapi import HTTPException, status

from app.features.auth.security import hash_password
from app.features.usuarios.schemas import CreateUsuarioRequest, UsuarioResponse
from app.features.usuarios.store import create_user


def criar_usuario(payload: CreateUsuarioRequest) -> UsuarioResponse:
    try:
        senha_hash = hash_password(payload.senha)
        user = create_user(
            nome=payload.nome.strip(),
            email=payload.email,
            telefone=payload.telefone.strip(),
            senha_hash=senha_hash,
        )
        return UsuarioResponse(
            id=user.id,
            nome=user.nome,
            email=user.email,
            telefone=user.telefone,
            criado_em=user.criado_em,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

