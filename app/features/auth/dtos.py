from typing import Literal

from pydantic import BaseModel, Field, field_validator


class LoginRequest(BaseModel):
    login_identifier: str = Field(min_length=3, max_length=255, alias="email")
    password: str = Field(min_length=1, max_length=255)

    model_config = {"populate_by_name": True}

    @field_validator("login_identifier")
    @classmethod
    def normalize_identifier(cls, value: str) -> str:
        return value.strip().lower()


class TokenResponse(BaseModel):
    access_token: str
    token_type: Literal["bearer"] = "bearer"


class MembershipClaim(BaseModel):
    membership_id: str
    empresa_id: str
    role: str
    is_default: bool = False


class AuthenticatedIdentity(BaseModel):
    auth_account_id: str
    user_id: str
    memberships: list[MembershipClaim] = []


class LoginResponse(TokenResponse):
    identity: AuthenticatedIdentity
