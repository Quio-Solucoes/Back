from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


OrcamentoStatus = Literal["draft", "in-progress", "completed"]


class OrcamentoResponse(BaseModel):
    id: str
    nome: str
    cliente: str
    arquiteto: str
    ambiente: str | None = None
    status: OrcamentoStatus
    criado_em: str
    atualizado_em: str


class CreateOrcamentoRequest(BaseModel):
    cliente: str = Field(min_length=1, max_length=120)
    arquiteto: str = Field(min_length=1, max_length=120)
    ambiente: str | None = Field(default=None, max_length=120)


class UpdateOrcamentoRequest(BaseModel):
    cliente: str | None = Field(default=None, min_length=1, max_length=120)
    arquiteto: str | None = Field(default=None, min_length=1, max_length=120)
    ambiente: str | None = Field(default=None, max_length=120)
    status: OrcamentoStatus | None = None

