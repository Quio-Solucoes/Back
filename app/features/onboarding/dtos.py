from pydantic import BaseModel, Field, field_validator


class CreateFranchiseInviteRequest(BaseModel):
    email: str = Field(min_length=3, max_length=255)
    expires_in_days: int = Field(default=7, ge=1, le=30)

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        return value.strip().lower()


class FranchiseInviteResponse(BaseModel):
    id: str
    email: str
    status: str
    expires_at: str
    registration_token: str | None = None


class CompanyAddressInput(BaseModel):
    street: str = Field(min_length=2, max_length=255)
    number: str | None = Field(default=None, max_length=20)
    complement: str | None = Field(default=None, max_length=100)
    district: str | None = Field(default=None, max_length=100)
    city: str = Field(min_length=2, max_length=100)
    state: str = Field(min_length=2, max_length=2)
    zip_code: str = Field(min_length=8, max_length=12)


class CompanyPhoneInput(BaseModel):
    label: str | None = Field(default=None, max_length=30)
    phone_number: str = Field(min_length=8, max_length=20)
    is_whatsapp: bool = False


class RegisterFranchiseRequest(BaseModel):
    invite_token: str = Field(min_length=20, max_length=255)
    razao_social: str = Field(min_length=2, max_length=255)
    nome_fantasia: str | None = Field(default=None, max_length=255)
    cnpj: str | None = Field(default=None, max_length=18)
    owner_name: str = Field(min_length=2, max_length=255)
    owner_email: str = Field(min_length=3, max_length=255)
    owner_password: str = Field(min_length=8, max_length=255)
    plan_id: str = Field(min_length=3, max_length=100)
    billing_cycle: str = Field(default="MONTHLY")
    address: CompanyAddressInput
    phone: CompanyPhoneInput

    @field_validator("billing_cycle")
    @classmethod
    def normalize_billing_cycle(cls, value: str) -> str:
        return value.strip().upper()

    @field_validator("owner_email")
    @classmethod
    def normalize_owner_email(cls, value: str) -> str:
        return value.strip().lower()


class InternalEmpresaActionResponse(BaseModel):
    empresa_id: str
    empresa_status: str
    owner_status: str | None = None
    subscription_status: str | None = None
