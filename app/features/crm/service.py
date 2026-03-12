from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.features.crm.dtos import ContractSignedRequest, LeadUpdateContractRequest, PreCadastroRequest
from app.features.crm.enums import ContractStatus, LeadStatus
from app.features.crm.repository import create_lead as repo_create_lead
from app.features.crm.repository import get_lead, list_leads, save
from app.features.invites.service import create_franchise_invite
from app.features.crm.dtos_nfe import EnableNfeRequest, EnableNfeResponse


def create_lead(db: Session, payload: PreCadastroRequest):
    return repo_create_lead(
        db,
        empresa_nome=payload.empresa_nome,
        contato_nome=payload.contato_nome,
        contato_email=payload.contato_email,
        contato_phone=payload.contato_phone,
        plano_id=payload.plano_id,
        vagas_contratadas=payload.vagas_contratadas,
        observacoes=payload.observacoes,
    )


def mark_contract_sent(db: Session, lead_id: str, payload: LeadUpdateContractRequest):
    lead = _require_lead(db, lead_id)
    lead.contract_status = ContractStatus.SENT
    lead.status = LeadStatus.CONTRACT_SENT
    lead.contract_sent_at = datetime.now(timezone.utc)
    if payload.contrato_url:
        lead.contrato_url = payload.contrato_url
    if payload.plano_id:
        lead.plano_id = payload.plano_id
    if payload.vagas_contratadas:
        lead.vagas_contratadas = payload.vagas_contratadas
    return save(db, lead)


def mark_contract_signed(db: Session, lead_id: str, payload: ContractSignedRequest):
    lead = _require_lead(db, lead_id)
    lead.contract_status = ContractStatus.SIGNED
    lead.status = LeadStatus.CONTRACT_SIGNED
    lead.contract_signed_at = datetime.now(timezone.utc)
    if payload.contrato_url:
        lead.contrato_url = payload.contrato_url

    invite, token = create_franchise_invite(db, lead.contato_email)
    db.refresh(invite)
    save(db, lead)
    return invite, token, lead


def list_all_leads(db: Session):
    return list_leads(db)


def enable_nfe(db: Session, lead_id: str, payload: EnableNfeRequest) -> EnableNfeResponse:
    lead = _require_lead(db, lead_id)
    lead.nfe_enabled = bool(payload.enable)
    save(db, lead)
    return EnableNfeResponse(lead_id=lead.id, nfe_enabled=lead.nfe_enabled)


def _require_lead(db: Session, lead_id: str):
    lead = get_lead(db, lead_id)
    if not lead:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lead nao encontrado")
    return lead
