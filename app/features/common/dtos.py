from pydantic import BaseModel, Field


class AddressInputDto(BaseModel):
    street: str = Field(min_length=2, max_length=255)
    number: str | None = Field(default=None, max_length=20)
    complement: str | None = Field(default=None, max_length=100)
    district: str | None = Field(default=None, max_length=100)
    city: str = Field(min_length=2, max_length=100)
    state: str = Field(min_length=2, max_length=2)
    zip_code: str = Field(min_length=8, max_length=12)


class PhoneInputDto(BaseModel):
    label: str | None = Field(default=None, max_length=30)
    phone_number: str = Field(min_length=8, max_length=20)
    is_whatsapp: bool = False


class AddressResponseDto(BaseModel):
    id: str
    street: str
    number: str | None
    complement: str | None
    district: str | None
    city: str
    state: str
    zip_code: str


class PhoneResponseDto(BaseModel):
    id: str
    label: str | None
    phone_number: str
    is_whatsapp: bool
