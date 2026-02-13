from dataclasses import dataclass, field

from app.features.ambientes.componentes.model import Componente


@dataclass
class Movel:
    id: int
    nome: str
    tipo: str
    material: str
    cor: str
    preco_base: float
    L_mm: float
    A_mm: float
    P_mm: float
    area: float
    descricao: str


@dataclass
class ConfiguracaoMovel:
    movel: Movel
    componentes: list[Componente] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.L_mm = self.movel.L_mm
        self.A_mm = self.movel.A_mm
        self.P_mm = self.movel.P_mm
        self.material = self.movel.material
        self.cor = self.movel.cor
        self.preco_atual = self.movel.preco_base

    @property
    def nome_movel(self) -> str:
        return self.movel.nome

    def area_atual(self) -> float:
        return (self.L_mm / 1000) * (self.P_mm / 1000)

    def recalcular_preco_por_area(self) -> None:
        fator = self.area_atual() / self.movel.area
        self.preco_atual = self.movel.preco_base * fator

    def total_componentes(self) -> float:
        return sum(c.total() for c in self.componentes)

    def total_geral(self) -> float:
        return self.preco_atual + self.total_componentes()

