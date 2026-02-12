from fastapi import HTTPException
from fastapi.responses import StreamingResponse

from app.features.conversations.store import get_conversa
from app.features.orcamento.services.pdf_service import gerar_pdf_orcamento


def download_pdf(session_id: str) -> StreamingResponse:
    conversa = get_conversa(session_id)

    if not conversa or not conversa.moveis_orcados:
        raise HTTPException(status_code=404, detail="Orcamento nao encontrado")

    try:
        buffer = gerar_pdf_orcamento(conversa.moveis_orcados, session_id)
        filename = f"orcamento_{session_id}.pdf"
        headers = {"Content-Disposition": f'attachment; filename="{filename}"'}
        return StreamingResponse(buffer, media_type="application/pdf", headers=headers)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


def status_orcamento(session_id: str) -> dict:
    conversa = get_conversa(session_id)

    if not conversa:
        raise HTTPException(status_code=404, detail="Sessao nao encontrada")

    return {
        "estado": conversa.estado,
        "qtd_moveis": len(conversa.moveis_orcados),
        "total": sum(m.total_geral() for m in conversa.moveis_orcados) if conversa.moveis_orcados else 0,
    }
