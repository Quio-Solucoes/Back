from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.db import get_db
from app.features.auth.dependencies import require_internal_api_key
from app.features.crm.dtos import (
    ContractSignedRequest,
    ContractSignedResponse,
    LeadResponse,
    LeadUpdateContractRequest,
    PreCadastroRequest,
)
from app.features.crm.dtos_nfe import EnableNfeRequest, EnableNfeResponse
from app.features.crm.service import (
    create_lead,
    enable_nfe,
    list_all_leads,
    mark_contract_signed,
    mark_contract_sent,
)


router = APIRouter(prefix="/crm", tags=["crm"])


@router.post("/pre-cadastro", response_model=LeadResponse, status_code=201)
def pre_cadastro(payload: PreCadastroRequest, db: Session = Depends(get_db)) -> LeadResponse:
    lead = create_lead(db, payload)
    return LeadResponse.from_model(lead)


@router.post("/leads/{lead_id}/contract/sent", response_model=LeadResponse)
def contract_sent(
    lead_id: str,
    payload: LeadUpdateContractRequest,
    db: Session = Depends(get_db),
    _: None = Depends(require_internal_api_key),
) -> LeadResponse:
    lead = mark_contract_sent(db, lead_id, payload)
    return LeadResponse.from_model(lead)


@router.post("/leads/{lead_id}/contract/signed", response_model=ContractSignedResponse)
def contract_signed(
    lead_id: str,
    payload: ContractSignedRequest,
    db: Session = Depends(get_db),
    _: None = Depends(require_internal_api_key),
) -> ContractSignedResponse:
    invite, token, lead = mark_contract_signed(db, lead_id, payload)
    # Na prática, enviar e-mail com o token para o contato. Aqui só retornamos.
    return ContractSignedResponse(
        lead_id=lead.id,
        franchise_invite_token=token,
        franchise_invite_id=invite.id,
        contato_email=lead.contato_email,
    )


@router.get("/leads", response_model=list[LeadResponse])
def list_leads(db: Session = Depends(get_db), _: None = Depends(require_internal_api_key)) -> list[LeadResponse]:
    leads = list_all_leads(db)
    return [LeadResponse.from_model(item) for item in leads]


@router.post("/leads/{lead_id}/nfe/enable", response_model=EnableNfeResponse)
def enable_lead_nfe(
    lead_id: str,
    payload: EnableNfeRequest,
    db: Session = Depends(get_db),
    _: None = Depends(require_internal_api_key),
) -> EnableNfeResponse:
    return enable_nfe(db, lead_id, payload)
