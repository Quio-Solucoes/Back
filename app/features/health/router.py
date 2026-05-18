from fastapi import APIRouter, Depends


router = APIRouter(tags=["health"])


@router.get("/health")
def health() -> dict:
    return {
        "status": "ok",
        "message": "Backend FastAPI rodando com sucesso!",
    }
