def listar_componentes(config) -> str:
    if not config.componentes:
        return "Componentes: nenhum configurado.\n"

    txt = "Componentes:\n"
    for c in config.componentes:
        txt += f"- {c.quantidade}x {c.nome} (R$ {c.total():.2f})\n"
    return txt


def gerar_resumo_configuracao(config) -> str:
    return (
        f"{config.movel.nome}\n\n"
        f"Dimensao: {int(config.L_mm)} x {int(config.A_mm)} x {int(config.P_mm)} mm\n"
        f"Area: {config.area_atual():.2f} m2\n"
        f"Material: {config.material}\n"
        f"Cor: {config.cor}\n\n"
        f"Preco movel: R$ {config.preco_atual:.2f}\n"
        f"{listar_componentes(config)}\n"
        f"Total: R$ {config.total_geral():.2f}"
    )


def resposta_com_opcoes(texto: str, opcoes: list[dict]) -> dict:
    return {
        "response": texto,
        "options": [{"id": o["id"], "label": o["label"]} for o in opcoes],
    }
