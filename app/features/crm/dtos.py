from pydantic import BaseModel, Field, field_validator


class PreCadastroRequest(BaseModel):
    empresa_nome: str = Field(min_length=2, max_length=255)
    contato_nome: str = Field(min_length=2, max_length=255)
    contato_email: str = Field(min_length=3, max_length=255)
    contato_phone: str | None = Field(default=None, max_length=30)
    plano_id: str | None = Field(default=None, max_length=32)
    vagas_contratadas: int | None = Field(default=None, ge=1)
    observacoes: str | None = Field(default=None, max_length=2000)

    @field_validator("contato_email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        return value.strip().lower()


class LeadResponse(BaseModel):
    id: str
    empresa_nome: str
    contato_nome: str
    contato_email: str
    contato_phone: str | None
    status: str
    contract_status: str
    contract_sent_at: str | None
    contract_signed_at: str | None
    plano_id: str | None
    vagas_contratadas: int | None

    @classmethod
    def from_model(cls, model) -> "LeadResponse":
        return cls(
            id=model.id,
            empresa_nome=model.empresa_nome,
            contato_nome=model.contato_nome,
            contato_email=model.contato_email,
            contato_phone=model.contato_phone,
            status=model.status.value,
            contract_status=model.contract_status.value,
            contract_sent_at=model.contract_sent_at.isoformat() if model.contract_sent_at else None,
            contract_signed_at=model.contract_signed_at.isoformat() if model.contract_signed_at else None,
            plano_id=model.plano_id,
            vagas_contratadas=model.vagas_contratadas,
        )


class LeadUpdateContractRequest(BaseModel):
    contrato_url: str | None = Field(default=None, max_length=1024)
    plano_id: str | None = Field(default=None, max_length=32)
    vagas_contratadas: int | None = Field(default=None, ge=1)


class ContractSignedRequest(BaseModel):
    contrato_url: str | None = Field(default=None, max_length=1024)


class ContractSignedResponse(BaseModel):
    lead_id: str
    franchise_invite_token: str
    franchise_invite_id: str
    contato_email: str
