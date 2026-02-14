from pydantic import BaseModel, Field


class EmpresaAddressPayload(BaseModel):
    street: str = Field(min_length=2, max_length=255)
    number: str | None = Field(default=None, max_length=20)
    complement: str | None = Field(default=None, max_length=100)
    district: str | None = Field(default=None, max_length=100)
    city: str = Field(min_length=2, max_length=100)
    state: str = Field(min_length=2, max_length=2)
    zip_code: str = Field(min_length=8, max_length=12)


class EmpresaPhonePayload(BaseModel):
    label: str | None = Field(default=None, max_length=30)
    phone_number: str = Field(min_length=8, max_length=20)
    is_whatsapp: bool = False


class EmpresaUpdateRequest(BaseModel):
    razao_social: str | None = Field(default=None, min_length=2, max_length=255)
    nome_fantasia: str | None = Field(default=None, max_length=255)
    cnpj: str | None = Field(default=None, max_length=18)
    address: EmpresaAddressPayload | None = None
    phone: EmpresaPhonePayload | None = None


class EmpresaAddressResponse(BaseModel):
    id: str
    street: str
    number: str | None
    complement: str | None
    district: str | None
    city: str
    state: str
    zip_code: str


class EmpresaPhoneResponse(BaseModel):
    id: str
    label: str | None
    phone_number: str
    is_whatsapp: bool


class EmpresaResponse(BaseModel):
    id: str
    razao_social: str
    nome_fantasia: str | None
    cnpj: str | None
    status: str
    addresses: list[EmpresaAddressResponse]
    phones: list[EmpresaPhoneResponse]

    @classmethod
    def from_model(cls, model) -> "EmpresaResponse":
        return cls(
            id=model.id,
            razao_social=model.razao_social,
            nome_fantasia=model.nome_fantasia,
            cnpj=model.cnpj,
            status=model.status.value,
            addresses=[
                EmpresaAddressResponse(
                    id=item.id,
                    street=item.street,
                    number=item.number,
                    complement=item.complement,
                    district=item.district,
                    city=item.city,
                    state=item.state,
                    zip_code=item.zip_code,
                )
                for item in model.addresses
            ],
            phones=[
                EmpresaPhoneResponse(
                    id=item.id,
                    label=item.label,
                    phone_number=item.phone_number,
                    is_whatsapp=item.is_whatsapp,
                )
                for item in model.phones
            ],
        )
