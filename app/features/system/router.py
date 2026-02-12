from fastapi import APIRouter

from app.features.system.service import download_pdf, status_orcamento

router = APIRouter(tags=["system"])


@router.get("/download-pdf/{session_id}")
def get_download_pdf(session_id: str):
    return download_pdf(session_id)


@router.get("/status/{session_id}")
def get_status_orcamento(session_id: str) -> dict:
    return status_orcamento(session_id)
