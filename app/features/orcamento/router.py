from fastapi import APIRouter, Depends

from app.features.auth.dependencies import get_current_user
from app.features.empresas.memberships.enums import MembershipRole
from app.features.users.schema import User
from app.features.orcamento.dtos import AtualizarComponenteRequest, EditarDimensaoRequest
from app.features.orcamento.service import (
    atualizar_componente,
    editar_componente,
    editar_dimensao,
    obter_orcamento,
    remover_movel,
    status_orcamento,
)

router = APIRouter(prefix="/orcamento", tags=["orcamento"])


@router.get("/{session_id}")
def get_orcamento(
    session_id: str,
    desconto_cliente_pct: float = 0.0,
    taxa_arquiteto_pct: float = 0.0,
    lucro_liquido_pct: float = 0.0,
    consultor_pct: float | None = None,
    current_user: User = Depends(get_current_user),
) -> dict:
    role = getattr(current_user, "role", MembershipRole.COLABORADOR)
    return obter_orcamento(
        session_id=session_id,
        desconto_cliente_pct=desconto_cliente_pct,
        taxa_arquiteto_pct=taxa_arquiteto_pct,
        user_role=role,
        lucro_liquido_pct=lucro_liquido_pct,
        consultor_pct=consultor_pct,
    )


@router.delete("/{session_id}/remover/{movel_id}")
def delete_movel(session_id: str, movel_id: int) -> dict:
    return remover_movel(session_id, movel_id)


@router.get("/{session_id}/editar-componente/{movel_id}/{componente_id}")
def get_editar_componente(session_id: str, movel_id: int, componente_id: int) -> dict:
    return editar_componente(session_id, movel_id, componente_id)


@router.post("/{session_id}/atualizar-componente/{movel_id}/{componente_id}")
def post_atualizar_componente(
    session_id: str,
    movel_id: int,
    componente_id: int,
    payload: AtualizarComponenteRequest,
) -> dict:
    return atualizar_componente(session_id, movel_id, componente_id, str(payload.opcao))


@router.post("/{session_id}/editar-dimensao/{movel_id}")
def post_editar_dimensao(session_id: str, movel_id: int, payload: EditarDimensaoRequest) -> dict:
    return editar_dimensao(
        session_id=session_id,
        movel_id=movel_id,
        largura=payload.largura,
        altura=payload.altura,
        profundidade=payload.profundidade,
    )

@router.get("/status/{session_id}")
def get_status_orcamento(session_id: str) -> dict:
    return status_orcamento(session_id)
