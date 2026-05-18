from pydantic import BaseModel, Field


class AdicionarItemRequest(BaseModel):
    produto_id: int = Field(..., ge=1)
    dimensao: str = ""
    cor: str = ""
    quantidade: int = Field(1, ge=1)
    vista_id: str = "frontal"

