from pydantic import BaseModel, Field

from app.features.common.dtos import PhoneInputDto, PhoneResponseDto

class UserPhoneCreateRequest(BaseModel):
    phone: PhoneInputDto
    is_primary: bool = False


class UserPhoneResponse(PhoneResponseDto):
    id: str

    @classmethod
    def from_model(cls, model) -> "UserPhoneResponse":
        return cls(
            id=model.id,
            label=model.label,
            phone_number=model.phone_number,
            is_whatsapp=model.is_whatsapp,
        )
