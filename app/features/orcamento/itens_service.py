from fastapi import HTTPException

from app.features.catalogo.repository import criar_item_por_etapas
from app.features.conversations.store import get_conversa


def obter_orcamento_itens(session_id: str) -> dict:
    conversa = get_conversa(session_id)

    if not conversa:
        return {"vistas": {}, "total": 0.0, "finalizado": False}

    vistas: dict[str, list[dict]] = {}
    total_geral = 0.0
    contador = 0

    for vista_id, lista in (conversa.itens_por_vista or {}).items():
        vistas[vista_id] = []
        for item in lista:
            subtotal = float(item.subtotal())
            total_geral += subtotal

            vistas[vista_id].append(
                {
                    "item_id": contador,
                    "produto_id": int(item.produto_id),
                    "produto": item.nome,
                    "dimensao": item.dimensao,
                    "cor": item.cor,
                    "quantidade": int(item.quantidade),
                    "preco_unitario": float(item.preco_unitario),
                    "subtotal": subtotal,
                }
            )
            contador += 1

    return {"vistas": vistas, "total": total_geral, "finalizado": bool(getattr(conversa, "finalizado", False))}


def remover_item(session_id: str, item_id: int) -> dict:
    conversa = get_conversa(session_id)
    if not conversa:
        raise HTTPException(status_code=404, detail="Sessao nao encontrada")

    contador = 0
    for vista_id, lista in list((conversa.itens_por_vista or {}).items()):
        for idx, _ in enumerate(list(lista)):
            if contador == item_id:
                lista.pop(idx)
                if not lista:
                    del conversa.itens_por_vista[vista_id]
                conversa.finalizado = False
                return {"success": True}
            contador += 1

    raise HTTPException(status_code=400, detail="Item invalido")


def editar_item(session_id: str, item_id: int, payload: dict) -> dict:
    conversa = get_conversa(session_id)
    if not conversa:
        raise HTTPException(status_code=404, detail="Sessao nao encontrada")

    produto_id = payload.get("produto_id")
    dimensao = payload.get("dimensao", "")
    cor = payload.get("cor", "")
    quantidade = int(payload.get("quantidade", 1))
    vista_id = payload.get("vista_id", None)

    if not produto_id:
        raise HTTPException(status_code=400, detail="produto_id obrigatorio")

    result = criar_item_por_etapas(int(produto_id), dimensao, cor, quantidade)
    if result.get("error"):
        raise HTTPException(status_code=404, detail=str(result["error"]))

    novo_item = result["item_obj"]

    contador = 0
    for vista_atual, lista in list((conversa.itens_por_vista or {}).items()):
        for idx, _ in enumerate(list(lista)):
            if contador == item_id:
                lista.pop(idx)
                if not lista:
                    del conversa.itens_por_vista[vista_atual]

                destino = vista_id or vista_atual
                conversa.itens_por_vista.setdefault(destino, []).append(novo_item)
                conversa.finalizado = False
                return {"success": True}
            contador += 1

    raise HTTPException(status_code=400, detail="Item invalido")

