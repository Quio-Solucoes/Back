from app.features.orcamento.catalogo import catalogo_repository


def listar_catalogo_componentes() -> dict[str, list[dict]]:
    return catalogo_repository.buscar_catalogo_componentes()


def buscar_movel_por_nome(nome: str):
    return catalogo_repository.buscar_movel_por_nome(nome)
