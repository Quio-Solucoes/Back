from fastapi import APIRouter

from app.features.orcamento.pdf.service import download_pdf_orcamento

router = APIRouter(prefix="/orcamento/pdf", tags=["orcamento-pdf"])


@router.get("/download/{session_id}")
def get_download_pdf_orcamento(session_id: str):
    return download_pdf_orcamento(session_id)
