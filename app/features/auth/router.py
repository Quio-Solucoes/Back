from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.features.auth.dtos import LoginRequest, LoginResponse
from app.features.auth.service import login
from app.db.db import get_db

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=LoginResponse)
def login_route(payload: LoginRequest, db: Session = Depends(get_db)) -> LoginResponse:
    return login(db=db, payload=payload)
