from fastapi import HTTPException
from fastapi.responses import StreamingResponse

from app.features.conversations.store import get_conversa
from app.features.orcamento.pdf.pdf_service import gerar_pdf_itens_orcamento, gerar_pdf_orcamento


def download_pdf(session_id: str) -> StreamingResponse:
    conversa = get_conversa(session_id)

    if not conversa:
        raise HTTPException(status_code=404, detail="Orcamento nao encontrado")

    try:
        if getattr(conversa, "itens_por_vista", None) and any(conversa.itens_por_vista.values()):
            buffer = gerar_pdf_itens_orcamento(conversa.itens_por_vista, session_id)
        elif getattr(conversa, "moveis_orcados", None):
            buffer = gerar_pdf_orcamento(conversa.moveis_orcados, session_id)
        else:
            raise HTTPException(status_code=404, detail="Orcamento nao encontrado")
        filename = f"orcamento_{session_id}.pdf"
        headers = {"Content-Disposition": f'attachment; filename="{filename}"'}
        return StreamingResponse(buffer, media_type="application/pdf", headers=headers)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


def status_orcamento(session_id: str) -> dict:
    conversa = get_conversa(session_id)

    if not conversa:
        raise HTTPException(status_code=404, detail="Sessao nao encontrada")

    itens_por_vista = getattr(conversa, "itens_por_vista", {}) or {}
    qtd_itens = sum(len(v) for v in itens_por_vista.values())
    total_itens = sum(i.subtotal() for v in itens_por_vista.values() for i in v) if itens_por_vista else 0.0

    return {
        "estado": getattr(conversa, "estado", "UNKNOWN"),
        "qtd_itens": qtd_itens,
        "total": float(total_itens),
    }
