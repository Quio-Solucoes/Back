from pathlib import Path

from fastapi import HTTPException
from fastapi.responses import FileResponse

from app.config.settings import ORCAMENTOS_DIR


def download_pdf_orcamento(session_id: str) -> FileResponse:
    base_dir = Path(ORCAMENTOS_DIR)
    if not base_dir.exists():
        raise HTTPException(status_code=404, detail="Nenhum PDF de orcamento encontrado")

    arquivos = sorted(
        base_dir.glob(f"orcamento_{session_id}_*.pdf"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )

    if not arquivos:
        raise HTTPException(status_code=404, detail="PDF do orcamento nao encontrado para esta sessao")

    arquivo = arquivos[0]
    return FileResponse(path=arquivo, media_type="application/pdf", filename=arquivo.name)
