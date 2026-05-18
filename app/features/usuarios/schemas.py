from datetime import datetime

from pydantic import AliasChoices, BaseModel, Field, field_validator


class CreateUsuarioRequest(BaseModel):
    nome: str = Field(min_length=1, max_length=120)
    email: str = Field(min_length=3, max_length=254)
    telefone: str = Field(min_length=8, max_length=30)
    senha: str = Field(min_length=8, max_length=256, validation_alias=AliasChoices("senha", "password"))

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        email = str(value or "").strip().lower()
        if "@" not in email or "." not in email.split("@")[-1]:
            raise ValueError("Email invalido")
        return email

    @field_validator("telefone")
    @classmethod
    def validate_telefone(cls, value: str) -> str:
        telefone = str(value or "").strip()
        digits = "".join(ch for ch in telefone if ch.isdigit())
        if len(digits) < 8:
            raise ValueError("Telefone invalido")
        return telefone


class UsuarioResponse(BaseModel):
    id: str
    nome: str
    email: str
    telefone: str
    criado_em: datetime
