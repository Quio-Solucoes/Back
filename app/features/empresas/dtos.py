from pydantic import BaseModel, Field

from app.features.common.dtos import AddressInputDto, AddressResponseDto, PhoneInputDto, PhoneResponseDto

class EmpresaAddressPayload(AddressInputDto):
    pass


class EmpresaPhonePayload(PhoneInputDto):
    pass


class EmpresaUpdateRequest(BaseModel):
    razao_social: str | None = Field(default=None, min_length=2, max_length=255)
    nome_fantasia: str | None = Field(default=None, max_length=255)
    cnpj: str | None = Field(default=None, max_length=18)
    address: EmpresaAddressPayload | None = None
    phone: EmpresaPhonePayload | None = None


class EmpresaAddressResponse(AddressResponseDto):
    pass


class EmpresaPhoneResponse(PhoneResponseDto):
    pass


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
