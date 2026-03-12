from pydantic import BaseModel, Field

from app.features.common.dtos import AddressInputDto, AddressResponseDto


class UserAddressCreateRequest(BaseModel):
    address: AddressInputDto
    label: str | None = Field(default=None, max_length=30)
    is_primary: bool = False


class UserAddressLinkResponse(BaseModel):
    address: AddressResponseDto
    label: str | None = None
    is_primary: bool

    @classmethod
    def from_model(cls, link) -> "UserAddressLinkResponse":
        a = link.address
        return cls(
            address=AddressResponseDto(
                id=a.id,
                street=a.street,
                number=a.number,
                complement=a.complement,
                district=a.district,
                city=a.city,
                state=a.state,
                zip_code=a.zip_code,
            ),
            label=link.label,
            is_primary=link.is_primary,
        )
