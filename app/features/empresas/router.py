from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.db import get_db
from app.features.auth.dependencies import get_current_user, require_internal_api_key, require_roles
from app.features.empresas.schemas import EmpresaResponse, EmpresaUpdateRequest
from app.features.empresas.service import list_empresas, require_empresa_with_contacts, update_empresa
from app.features.users.enums import UserRole
from app.features.users.models import User


router = APIRouter(prefix="/empresas", tags=["empresas"])


@router.get("/me", response_model=EmpresaResponse)
def get_my_company(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> EmpresaResponse:
    empresa = require_empresa_with_contacts(db, current_user.empresa_id)
    return EmpresaResponse.from_model(empresa)


@router.patch("/me", response_model=EmpresaResponse)
def update_my_company(
    payload: EmpresaUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.OWNER, UserRole.ADMIN)),
) -> EmpresaResponse:
    empresa = require_empresa_with_contacts(db, current_user.empresa_id)
    updated = update_empresa(db, empresa, payload)
    return EmpresaResponse.from_model(updated)


@router.get("/internal", response_model=list[EmpresaResponse])
def list_all_companies(
    db: Session = Depends(get_db),
    _: None = Depends(require_internal_api_key),
) -> list[EmpresaResponse]:
    empresas = list_empresas(db)
    return [EmpresaResponse.from_model(item) for item in empresas]
