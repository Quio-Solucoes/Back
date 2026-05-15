from fastapi import APIRouter, HTTPException, Request

from app.features.system.service import download_pdf, status_orcamento
from app.config.settings import APP_ENV, FOTOS_DIR

router = APIRouter(tags=["system"])


@router.get("/download-pdf/{session_id}")
def get_download_pdf(session_id: str):
    return download_pdf(session_id)


@router.get("/status/{session_id}")
def get_status_orcamento(session_id: str) -> dict:
    return status_orcamento(session_id)


@router.get("/_debug/routes")
def get_debug_routes(request: Request) -> dict:
    if APP_ENV in {"prod", "production"}:
        raise HTTPException(status_code=404, detail="Not Found")

    routes: list[dict] = []
    for r in request.app.routes:
        path = getattr(r, "path", None)
        if not path:
            continue
        methods = getattr(r, "methods", None)
        routes.append(
            {
                "path": path,
                "name": getattr(r, "name", ""),
                "methods": sorted(list(methods)) if methods else [],
            }
        )

    routes.sort(key=lambda x: x["path"])
    return {"env": APP_ENV, "routes": routes}


@router.get("/_debug/fotos")
def get_debug_fotos() -> dict:
    if APP_ENV in {"prod", "production"}:
        raise HTTPException(status_code=404, detail="Not Found")

    if not FOTOS_DIR.exists():
        return {"env": APP_ENV, "fotos_dir": str(FOTOS_DIR), "exists": False, "files": []}

    files = sorted([p.name for p in FOTOS_DIR.iterdir() if p.is_file()])
    return {
        "env": APP_ENV,
        "fotos_dir": str(FOTOS_DIR),
        "exists": True,
        "count": len(files),
        "sample": files[:25],
    }
