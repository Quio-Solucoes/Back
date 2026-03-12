
from dataclasses import dataclass, field
from typing import Optional

from app.features.chat.enum_states import ESTADOS
from app.features.orcamento.ambientes.moveis.model import ConfiguracaoMovel


@dataclass
class Conversa:
    estado: str = ESTADOS["INICIO"]
    configuracao: Optional[ConfiguracaoMovel] = None
    categoria_selecionada: Optional[str] = None
    moveis_orcados: list[ConfiguracaoMovel] = field(default_factory=list)
