
from dataclasses import dataclass


@dataclass
class Conversa:
    estado: str = ESTADOS["INICIO"]
    configuracao: Optional[ConfiguracaoMovel] = None
    categoria_selecionada: Optional[str] = None
    moveis_orcados: list[ConfiguracaoMovel] = field(default_factory=list)