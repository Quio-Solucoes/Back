from pydantic import BaseModel


class AtualizarComponenteRequest(BaseModel):
    opcao: str


class EditarDimensaoRequest(BaseModel):
    largura: float
    altura: float
    profundidade: float
