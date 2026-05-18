from dataclasses import dataclass

from fastapi import HTTPException

from app.features.catalogo.repository import criar_item_por_etapas
from app.features.orcamentos.session_store import get_sessao
from app.features.orcamentos.store import delete_orcamento_item, list_orcamento_itens, update_orcamento_item


@dataclass(frozen=True)
class ItemOrcamentoPersistido:
    produto_nome: str
    dimensao: str
    cor: str
    quantidade: int
    preco_unitario: float

    @property
    def nome(self) -> str:
        return self.produto_nome

    def subtotal(self) -> float:
        return float(self.preco_unitario) * int(self.quantidade or 0)


def obter_orcamento_itens(session_id: str, *, user_id: str) -> dict:
    itens = list_orcamento_itens(orcamento_id=session_id, user_id=user_id)

    if itens:
        vistas: dict[str, list[dict]] = {}
        total_geral = 0.0

        for idx, row in enumerate(itens):
            subtotal = float(row["preco_unitario"]) * int(row["quantidade"] or 0)
            total_geral += subtotal

            vista_id = str(row.get("vista_id") or "frontal")
            vistas.setdefault(vista_id, []).append(
                {
                    "item_id": idx,
                    "produto_id": int(row["produto_id"]),
                    "produto": str(row["produto_nome"]),
                    "dimensao": str(row.get("dimensao") or ""),
                    "cor": str(row.get("cor") or ""),
                    "quantidade": int(row["quantidade"]),
                    "preco_unitario": float(row["preco_unitario"]),
                    "subtotal": float(subtotal),
                }
            )

        conversa = get_sessao(session_id)
        return {"vistas": vistas, "total": float(total_geral), "finalizado": bool(getattr(conversa, "finalizado", False)) if conversa else False}

    conversa = get_sessao(session_id)
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


def remover_item(session_id: str, item_id: int, *, user_id: str) -> dict:
    itens = list_orcamento_itens(orcamento_id=session_id, user_id=user_id)
    if itens:
        if item_id < 0 or item_id >= len(itens):
            raise HTTPException(status_code=400, detail="Item invalido")

        deleted = delete_orcamento_item(item_id=str(itens[item_id]["id"]), user_id=user_id)
        if not deleted:
            raise HTTPException(status_code=400, detail="Item invalido")

        # Mantém compatibilidade com estado em memória (se existir), mas não depende dele.
        conversa = get_sessao(session_id)
        if conversa:
            conversa.finalizado = False
        return {"success": True}

    conversa = get_sessao(session_id)
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


def editar_item(session_id: str, item_id: int, payload: dict, *, user_id: str) -> dict:
    conversa = get_sessao(session_id)
    itens = list_orcamento_itens(orcamento_id=session_id, user_id=user_id)
    if itens and (item_id < 0 or item_id >= len(itens)):
        raise HTTPException(status_code=400, detail="Item invalido")
    if not conversa and not itens:
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

    if itens:
        target = itens[item_id]
        destino = vista_id or str(target.get("vista_id") or "frontal")
        updated = update_orcamento_item(
            item_id=str(target["id"]),
            user_id=user_id,
            vista_id=destino,
            produto_id=int(novo_item.produto_id),
            produto_nome=str(novo_item.nome),
            dimensao=str(novo_item.dimensao),
            cor=str(novo_item.cor),
            quantidade=int(novo_item.quantidade),
            preco_unitario=float(novo_item.preco_unitario),
        )
        if not updated:
            raise HTTPException(status_code=400, detail="Item invalido")
        if conversa:
            conversa.finalizado = False
        return {"success": True}

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
