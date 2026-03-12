from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import DateTime, Enum, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.db import Base
from app.features.crm.enums import ContractStatus, LeadStatus


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class CrmLead(Base):
    __tablename__ = "crm_leads"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    empresa_nome: Mapped[str] = mapped_column(String(255), nullable=False)
    contato_nome: Mapped[str] = mapped_column(String(255), nullable=False)
    contato_email: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    contato_phone: Mapped[str | None] = mapped_column(String(30), nullable=True)
    plano_id: Mapped[str | None] = mapped_column(String(32), nullable=True)
    vagas_contratadas: Mapped[int | None] = mapped_column(Integer, nullable=True)
    observacoes: Mapped[str | None] = mapped_column(Text, nullable=True)
    contrato_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    status: Mapped[LeadStatus] = mapped_column(Enum(LeadStatus, name="crm_lead_status"), default=LeadStatus.NEW, nullable=False)
    contract_status: Mapped[ContractStatus] = mapped_column(
        Enum(ContractStatus, name="crm_contract_status"),
        default=ContractStatus.DRAFT,
        nullable=False,
    )
    nfe_enabled: Mapped[bool] = mapped_column(default=False, nullable=False)
    contract_sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    contract_signed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False
    )
