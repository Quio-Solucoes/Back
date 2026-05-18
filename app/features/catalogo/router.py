from fastapi import APIRouter, Depends, HTTPException, Query

from app.features.catalogo.repository import (
    buscar_produtos_por_termo,
    buscar_variantes_produto,
    criar_item_por_etapas,
)
from app.features.catalogo.schemas import AdicionarItemRequest
from app.features.orcamentos.session_store import get_or_create_sessao
from app.features.auth.dependencies import require_permission
from app.domain.models import Usuario
from app.features.orcamentos.store import create_orcamento_item, get_orcamento


router = APIRouter(tags=["catalogo"], dependencies=[Depends(require_permission)])


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
def post_adicionar_item(session_id: str, payload: AdicionarItemRequest, user: Usuario = Depends(require_permission)) -> dict:
    # `session_id` aqui é o id do orçamento persistido (mesmo valor usado em /orcamento/{session_id}).
    if not get_orcamento(orcamento_id=session_id, user_id=user.id):
        raise HTTPException(status_code=404, detail="Orcamento nao encontrado")

    conversa = get_or_create_sessao(session_id)
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

    try:
        create_orcamento_item(
            orcamento_id=session_id,
            user_id=user.id,
            vista_id=conversa.vista_atual,
            produto_id=int(item.produto_id),
            produto_nome=str(item.nome),
            dimensao=str(item.dimensao),
            cor=str(item.cor),
            quantidade=int(item.quantidade),
            preco_unitario=float(item.preco_unitario),
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return {"success": True}

