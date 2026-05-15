from fastapi import APIRouter

from app.features.orcamento.itens_service import editar_item, obter_orcamento_itens, remover_item

router = APIRouter(prefix="/orcamento", tags=["orcamento"])


@router.get("/{session_id}")
def get_orcamento(session_id: str) -> dict:
    return obter_orcamento_itens(session_id)


@router.delete("/{session_id}/remover/{item_id}")
def delete_item(session_id: str, item_id: int) -> dict:
    return remover_item(session_id, item_id)


@router.put("/{session_id}/editar-item/{item_id}")
def put_editar_item(session_id: str, item_id: int, payload: dict) -> dict:
    return editar_item(session_id, item_id, payload)
