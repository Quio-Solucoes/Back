from fastapi import APIRouter, Depends

from app.features.orcamentos.schemas import CreateOrcamentoRequest, OrcamentoResponse, UpdateOrcamentoRequest
from app.features.orcamentos.service import (
    atualizar_orcamento,
    criar_orcamento,
    listar_orcamentos,
    obter_orcamento,
    remover_orcamento,
)
from app.features.orcamentos.itens_service import editar_item, obter_orcamento_itens, remover_item
from app.features.auth.dependencies import require_permission
from app.domain.models import Usuario


router = APIRouter(prefix="/orcamentos", tags=["orcamentos"], dependencies=[Depends(require_permission)])
orcamento_router = APIRouter(prefix="/orcamento", tags=["orcamento"], dependencies=[Depends(require_permission)])


@router.get("", response_model=list[OrcamentoResponse])
def get_orcamentos(user: Usuario = Depends(require_permission)) -> list[OrcamentoResponse]:
    return listar_orcamentos(user_id=user.id)


@router.post("", response_model=OrcamentoResponse)
def post_orcamento(payload: CreateOrcamentoRequest, user: Usuario = Depends(require_permission)) -> OrcamentoResponse:
    return criar_orcamento(payload=payload, user_id=user.id)


@router.get("/{orcamento_id}", response_model=OrcamentoResponse)
def get_orcamento(orcamento_id: str, user: Usuario = Depends(require_permission)) -> OrcamentoResponse:
    return obter_orcamento(orcamento_id=orcamento_id, user_id=user.id)


@router.patch("/{orcamento_id}", response_model=OrcamentoResponse)
def patch_orcamento(orcamento_id: str, payload: UpdateOrcamentoRequest, user: Usuario = Depends(require_permission)) -> OrcamentoResponse:
    return atualizar_orcamento(orcamento_id=orcamento_id, payload=payload, user_id=user.id)


@router.delete("/{orcamento_id}")
def delete_orcamento(orcamento_id: str, user: Usuario = Depends(require_permission)) -> dict:
    return remover_orcamento(orcamento_id=orcamento_id, user_id=user.id)


@orcamento_router.get("/{session_id}")
def get_orcamento(session_id: str, user: Usuario = Depends(require_permission)) -> dict:
    return obter_orcamento_itens(session_id, user_id=user.id)


@orcamento_router.delete("/{session_id}/remover/{item_id}")
def delete_item(session_id: str, item_id: int, user: Usuario = Depends(require_permission)) -> dict:
    return remover_item(session_id, item_id, user_id=user.id)


@orcamento_router.put("/{session_id}/editar-item/{item_id}")
def put_editar_item(session_id: str, item_id: int, payload: dict, user: Usuario = Depends(require_permission)) -> dict:
    return editar_item(session_id, item_id, payload, user_id=user.id)
