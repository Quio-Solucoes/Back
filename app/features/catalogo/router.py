from fastapi import APIRouter, HTTPException, Query

from app.features.catalogo.repository import (
    buscar_produtos_por_termo,
    buscar_variantes_produto,
    criar_item_por_etapas,
)
from app.features.catalogo.schemas import AdicionarItemRequest
from app.features.conversations.store import get_or_create_conversa


router = APIRouter(tags=["catalogo"])


@router.get("/catalogo")
def get_catalogo(q: str = Query(default="", min_length=0)) -> list[dict]:
    return buscar_produtos_por_termo(q)


@router.get("/catalogo/variantes/{produto_id}")
def get_variantes(produto_id: int) -> dict:
    data = buscar_variantes_produto(produto_id)
    if not data:
        raise HTTPException(status_code=404, detail="Produto nao encontrado")
    return data


@router.post("/catalogo/adicionar/{session_id}")
def post_adicionar_item(session_id: str, payload: AdicionarItemRequest) -> dict:
    conversa = get_or_create_conversa(session_id)
    conversa.vista_atual = payload.vista_id or "frontal"

    result = criar_item_por_etapas(
        produto_id=payload.produto_id,
        dimensao=payload.dimensao,
        cor=payload.cor,
        quantidade=payload.quantidade,
    )

    if result.get("error"):
        raise HTTPException(status_code=404, detail=str(result["error"]))

    item = result["item_obj"]
    conversa.itens_por_vista.setdefault(conversa.vista_atual, []).append(item)
    conversa.finalizado = False

    return {"success": True}

