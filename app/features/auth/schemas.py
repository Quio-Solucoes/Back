from pydantic import AliasChoices, BaseModel, Field, field_validator


class LoginRequest(BaseModel):
    email: str = Field(min_length=3, max_length=254, validation_alias=AliasChoices("email", "username"))
    senha: str = Field(min_length=1, max_length=256, validation_alias=AliasChoices("senha", "password"))

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        return str(value or "").strip().lower()


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
