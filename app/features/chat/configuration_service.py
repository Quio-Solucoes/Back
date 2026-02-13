
from app.features.ambientes.moveis.model import ConfiguracaoMovel
from app.features.orcamento.catalog.repository import buscar_componentes_do_movel


def criar_configuracao_padrao(movel):
    config = ConfiguracaoMovel(movel)
    config.componentes = buscar_componentes_do_movel(movel.id)
    return config
