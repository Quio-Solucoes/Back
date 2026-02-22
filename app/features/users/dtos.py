from pydantic import BaseModel, Field, field_validator


class UserResponse(BaseModel):
    id: str
    empresa_id: str
    name: str
    email: str
    role: str
    status: str

    @classmethod
    def from_model(cls, model) -> "UserResponse":
        return cls(
            id=model.id,
            empresa_id=model.empresa_id,
            name=model.name,
            email=model.email,
            role=model.role.value,
            status=model.status.value,
        )


class CreateUserInviteRequest(BaseModel):
    email: str = Field(min_length=3, max_length=255)
    role: str = Field(pattern="^(ADMIN|MEMBER)$")
    expires_in_days: int = Field(default=7, ge=1, le=30)

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        return value.strip().lower()


class UserInviteResponse(BaseModel):
    id: str
    empresa_id: str
    email: str
    role: str
    status: str
    expires_at: str
    invitation_token: str | None = None


class AcceptUserInviteRequest(BaseModel):
    invite_token: str = Field(min_length=20, max_length=255)
    name: str = Field(min_length=2, max_length=255)
    password: str = Field(min_length=8, max_length=255)


class UpdateUserStatusRequest(BaseModel):
    status: str = Field(pattern="^(ACTIVE|SUSPENDED)$")
