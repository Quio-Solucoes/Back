from app.core.models import ConfiguracaoMovel
from app.core.repositories import buscar_componentes_do_movel


def criar_configuracao_padrao(movel):
    config = ConfiguracaoMovel(movel)
    config.componentes = buscar_componentes_do_movel(movel.id)
    return config

