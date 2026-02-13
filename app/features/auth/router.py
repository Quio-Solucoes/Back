from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.features.auth.schemas import LoginRequest, TokenResponse
from app.features.auth.service import login
from app.db.db import get_db

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
def login_route(payload: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    return login(db=db, payload=payload)
