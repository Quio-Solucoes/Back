from __future__ import annotations

from fastapi import HTTPException

from app.features.orcamentos.schemas import CreateOrcamentoRequest, OrcamentoResponse, UpdateOrcamentoRequest
from app.features.orcamentos.store import create_orcamento, delete_orcamento, get_orcamento, list_orcamentos, update_orcamento


def _to_response(row: dict) -> OrcamentoResponse:
    row.pop("user_id", None)
    return OrcamentoResponse(**row)


def listar_orcamentos(*, user_id: str) -> list[OrcamentoResponse]:
    return [_to_response(row) for row in list_orcamentos(user_id=user_id)]


def criar_orcamento(*, payload: CreateOrcamentoRequest, user_id: str) -> OrcamentoResponse:
    try:
        row = create_orcamento(user_id=user_id, cliente=payload.cliente, arquiteto=payload.arquiteto, ambiente=payload.ambiente)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return _to_response(row)


def obter_orcamento(*, orcamento_id: str, user_id: str) -> OrcamentoResponse:
    row = get_orcamento(orcamento_id=orcamento_id, user_id=user_id)
    if not row:
        raise HTTPException(status_code=404, detail="Orcamento nao encontrado")
    return _to_response(row)


def atualizar_orcamento(*, orcamento_id: str, payload: UpdateOrcamentoRequest, user_id: str) -> OrcamentoResponse:
    try:
        row = update_orcamento(
            orcamento_id=orcamento_id,
            user_id=user_id,
            cliente=payload.cliente,
            arquiteto=payload.arquiteto,
            ambiente=payload.ambiente,
            status=payload.status,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    if not row:
        raise HTTPException(status_code=404, detail="Orcamento nao encontrado")
    return _to_response(row)


def remover_orcamento(*, orcamento_id: str, user_id: str) -> dict:
    deleted = delete_orcamento(orcamento_id=orcamento_id, user_id=user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Orcamento nao encontrado")
    return {"success": True}
