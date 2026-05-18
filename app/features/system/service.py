from fastapi import HTTPException
from fastapi.responses import StreamingResponse

from app.features.orcamentos.session_store import get_sessao
from app.features.orcamentos.store import get_orcamento, list_orcamento_itens
from app.features.orcamentos.pdf.pdf_service import gerar_pdf_itens_orcamento, gerar_pdf_orcamento
from app.features.orcamentos.itens_service import ItemOrcamentoPersistido


def download_pdf(session_id: str, *, user_id: str) -> StreamingResponse:
    if not get_orcamento(orcamento_id=session_id, user_id=user_id):
        raise HTTPException(status_code=404, detail="Orcamento nao encontrado")

    itens = list_orcamento_itens(orcamento_id=session_id, user_id=user_id)
    if itens:
        itens_por_vista: dict[str, list[ItemOrcamentoPersistido]] = {}
        for row in itens:
            vista_id = str(row.get("vista_id") or "frontal")
            itens_por_vista.setdefault(vista_id, []).append(
                ItemOrcamentoPersistido(
                    produto_nome=str(row.get("produto_nome") or ""),
                    dimensao=str(row.get("dimensao") or ""),
                    cor=str(row.get("cor") or ""),
                    quantidade=int(row.get("quantidade") or 0),
                    preco_unitario=float(row.get("preco_unitario") or 0.0),
                )
            )

        # Prioriza sempre itens persistidos (mesmo que vazio, o PDF sai com "Nenhum item").
        buffer = gerar_pdf_itens_orcamento(itens_por_vista, session_id)
        filename = f"orcamento_{session_id}.pdf"
        headers = {"Content-Disposition": f'attachment; filename="{filename}"'}
        return StreamingResponse(buffer, media_type="application/pdf", headers=headers)

    conversa = get_sessao(session_id)
    if not conversa:
        raise HTTPException(status_code=404, detail="Orcamento nao encontrado")

    try:
        if getattr(conversa, "itens_por_vista", None) and any(conversa.itens_por_vista.values()):
            buffer = gerar_pdf_itens_orcamento(conversa.itens_por_vista, session_id)
        elif getattr(conversa, "moveis_orcados", None):
            buffer = gerar_pdf_orcamento(conversa.moveis_orcados, session_id)
        else:
            buffer = gerar_pdf_itens_orcamento({}, session_id)
        filename = f"orcamento_{session_id}.pdf"
        headers = {"Content-Disposition": f'attachment; filename="{filename}"'}
        return StreamingResponse(buffer, media_type="application/pdf", headers=headers)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


def status_orcamento(session_id: str, *, user_id: str) -> dict:
    if not get_orcamento(orcamento_id=session_id, user_id=user_id):
        raise HTTPException(status_code=404, detail="Sessao nao encontrada")

    itens = list_orcamento_itens(orcamento_id=session_id, user_id=user_id)
    if itens:
        qtd_itens = len(itens)
        total_itens = sum(float(i["preco_unitario"]) * int(i["quantidade"] or 0) for i in itens)
        conversa = get_sessao(session_id)
        return {
            "estado": getattr(conversa, "estado", "PERSISTED") if conversa else "PERSISTED",
            "qtd_itens": int(qtd_itens),
            "total": float(total_itens),
        }

    conversa = get_sessao(session_id)
    if not conversa:
        return {"estado": "PERSISTED", "qtd_itens": 0, "total": 0.0}

    itens_por_vista = getattr(conversa, "itens_por_vista", {}) or {}
    qtd_itens = sum(len(v) for v in itens_por_vista.values())
    total_itens = sum(i.subtotal() for v in itens_por_vista.values() for i in v) if itens_por_vista else 0.0

    return {
        "estado": getattr(conversa, "estado", "UNKNOWN"),
        "qtd_itens": qtd_itens,
        "total": float(total_itens),
    }
