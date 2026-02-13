from dataclasses import dataclass
from typing import Optional


@dataclass
class Componente:
    nome: str
    categoria_funcional: str
    quantidade: int
    preco_unitario: float
    material: Optional[str] = None
    cor: Optional[str] = None

    def total(self) -> float:
        return self.quantidade * self.preco_unitario