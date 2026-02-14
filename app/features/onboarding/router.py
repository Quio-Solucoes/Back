from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.db import get_db
from app.features.auth.dependencies import require_internal_api_key
from app.features.invites.service import create_franchise_invite, list_franchise_invites
from app.features.onboarding.schemas import (
    CreateFranchiseInviteRequest,
    FranchiseInviteResponse,
    InternalEmpresaActionResponse,
    RegisterFranchiseRequest,
)
from app.features.onboarding.service import (
    activate_owner_after_payment,
    approve_empresa,
    create_pending_company_and_owner,
    reject_empresa,
)


router = APIRouter(tags=["onboarding"])


@router.post("/internal/franchise-invites", response_model=FranchiseInviteResponse)
def create_invite(
    payload: CreateFranchiseInviteRequest,
    db: Session = Depends(get_db),
    _: None = Depends(require_internal_api_key),
) -> FranchiseInviteResponse:
    invite, token = create_franchise_invite(db, payload.email, payload.expires_in_days)
    return FranchiseInviteResponse(
        id=invite.id,
        email=invite.email,
        status=invite.status.value,
        expires_at=invite.expires_at.isoformat(),
        registration_token=token,
    )


@router.get("/internal/franchise-invites", response_model=list[FranchiseInviteResponse])
def list_invites(
    db: Session = Depends(get_db),
    _: None = Depends(require_internal_api_key),
) -> list[FranchiseInviteResponse]:
    invites = list_franchise_invites(db)
    return [
        FranchiseInviteResponse(
            id=invite.id,
            email=invite.email,
            status=invite.status.value,
            expires_at=invite.expires_at.isoformat(),
            registration_token=None,
        )
        for invite in invites
    ]


@router.post("/onboarding/register")
def register_franchise(payload: RegisterFranchiseRequest, db: Session = Depends(get_db)) -> dict[str, str]:
    try:
        empresa, owner, subscription = create_pending_company_and_owner(db, payload)
    except KeyError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="billing_cycle invalido. Use MONTHLY ou YEARLY",
        ) from exc

    return {
        "message": "Cadastro recebido. Aguarde validacao interna e compensacao do pagamento.",
        "empresa_id": empresa.id,
        "owner_user_id": owner.id,
        "subscription_id": subscription.id,
    }


@router.post("/internal/empresas/{empresa_id}/approve", response_model=InternalEmpresaActionResponse)
def approve(
    empresa_id: str,
    db: Session = Depends(get_db),
    _: None = Depends(require_internal_api_key),
) -> InternalEmpresaActionResponse:
    empresa, owner, subscription = approve_empresa(db, empresa_id)
    return InternalEmpresaActionResponse(
        empresa_id=empresa.id,
        empresa_status=empresa.status.value,
        owner_status=owner.status.value if owner else None,
        subscription_status=subscription.status.value if subscription else None,
    )


@router.post("/internal/empresas/{empresa_id}/reject", response_model=InternalEmpresaActionResponse)
def reject(
    empresa_id: str,
    db: Session = Depends(get_db),
    _: None = Depends(require_internal_api_key),
) -> InternalEmpresaActionResponse:
    empresa, owner, subscription = reject_empresa(db, empresa_id)
    return InternalEmpresaActionResponse(
        empresa_id=empresa.id,
        empresa_status=empresa.status.value,
        owner_status=owner.status.value if owner else None,
        subscription_status=subscription.status.value if subscription else None,
    )


@router.post("/internal/empresas/{empresa_id}/activate-owner", response_model=InternalEmpresaActionResponse)
def activate_owner(
    empresa_id: str,
    db: Session = Depends(get_db),
    _: None = Depends(require_internal_api_key),
) -> InternalEmpresaActionResponse:
    empresa, owner, subscription = activate_owner_after_payment(db, empresa_id)
    return InternalEmpresaActionResponse(
        empresa_id=empresa.id,
        empresa_status=empresa.status.value,
        owner_status=owner.status.value,
        subscription_status=subscription.status.value if subscription else None,
    )
