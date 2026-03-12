from pydantic import BaseModel, Field


class AddressInputDto(BaseModel):
    street: str = Field(..., max_length=255)
    number: str | None = Field(default=None, max_length=20)
    complement: str | None = Field(default=None, max_length=100)
    district: str | None = Field(default=None, max_length=100)
    city: str = Field(..., max_length=100)
    state: str = Field(..., min_length=2, max_length=2)
    zip_code: str = Field(..., max_length=12)


class AddressResponseDto(AddressInputDto):
    id: str

    class Config:
        from_attributes = True


class PhoneInputDto(BaseModel):
    label: str | None = Field(default=None, max_length=30)
    phone_number: str = Field(..., max_length=20)
    is_whatsapp: bool = False


class PhoneResponseDto(PhoneInputDto):
    id: str
    is_primary: bool = True

    class Config:
        from_attributes = True
