from sqlalchemy import select
from sqlalchemy.orm import Session

from app.features.crm.enums import ContractStatus, LeadStatus
from app.features.crm.schema import CrmLead


def create_lead(
    db: Session,
    *,
    empresa_nome: str,
    contato_nome: str,
    contato_email: str,
    contato_phone: str | None,
    plano_id: str | None,
    vagas_contratadas: int | None,
    observacoes: str | None,
) -> CrmLead:
    lead = CrmLead(
        empresa_nome=empresa_nome,
        contato_nome=contato_nome,
        contato_email=contato_email,
        contato_phone=contato_phone,
        plano_id=plano_id,
        vagas_contratadas=vagas_contratadas,
        observacoes=observacoes,
        status=LeadStatus.NEW,
        contract_status=ContractStatus.DRAFT,
    )
    db.add(lead)
    db.commit()
    db.refresh(lead)
    return lead


def list_leads(db: Session) -> list[CrmLead]:
    stmt = select(CrmLead).order_by(CrmLead.created_at.desc())
    return list(db.scalars(stmt).all())


def get_lead(db: Session, lead_id: str) -> CrmLead | None:
    return db.get(CrmLead, lead_id)


def save(db: Session, lead: CrmLead) -> CrmLead:
    db.add(lead)
    db.commit()
    db.refresh(lead)
    return lead
