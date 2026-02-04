from models import ConfiguracaoMovel
from repositories import buscar_componentes_do_movel


def criar_configuracao_padrao(movel):
    config = ConfiguracaoMovel(movel)
    config.componentes = buscar_componentes_do_movel(movel.id)
    return config