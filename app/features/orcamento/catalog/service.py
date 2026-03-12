from app.features.orcamento.catalog import repository


def buscar_componentes_do_movel(movel_id: int):
    return repository.buscar_componentes_do_movel(movel_id)
