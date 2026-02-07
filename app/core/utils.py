from __future__ import annotations


def listar_componentes(config):
    if not config.componentes:
        return "?? Nenhum componente configurado.\n"

    txt = "?? Componentes:\n"
    for c in config.componentes:
        txt += f"- {c.quantidade}x {c.nome} (R$ {c.total():.2f})\n"
    return txt


def gerar_resumo_configuracao(config):
    return (
        f"?? {config.movel.nome}\n\n"
        f"?? Dimensão: {int(config.L_mm)} x {int(config.A_mm)} x {int(config.P_mm)} mm\n"
        f"?? Área: {config.area_atual():.2f} m²\n"
        f"?? Material: {config.material}\n"
        f"?? Cor: {config.cor}\n\n"
        f"?? Preço móvel: R$ {config.preco_atual:.2f}\n"
        f"{listar_componentes(config)}\n"
        f"?? Total: R$ {config.total_geral():.2f}"
    )


def resposta_com_opcoes(texto, opcoes):
    return {
        "response": texto,
        "options": [{"id": o["id"], "label": o["label"]} for o in opcoes],
    }

