import unicodedata


def normalizar(txt: str) -> str:
    txt = txt.lower().strip()
    txt = unicodedata.normalize("NFD", txt)
    txt = "".join(c for c in txt if unicodedata.category(c) != "Mn")
    if txt.endswith("s"):
        txt = txt[:-1]
    return txt

def gerar_tabela_moveis_orcados(moveis: list) -> str:
    if not moveis:
        return "Nenhum movel orcado ainda."

    texto = "MOVEIS ORCADOS:\n\n"

    for idx, config in enumerate(moveis, 1):
        total = config.total_geral()
        texto += f"{idx}. {config.nome_movel}\n"
        texto += f"   Dimensoes: {config.L_mm}x{config.A_mm}x{config.P_mm} mm\n"
        texto += f"   Cor: {config.cor} | Material: {config.material}\n"
        texto += f"   Valor: R$ {total:.2f}\n\n"

    total_geral = sum(m.total_geral() for m in moveis)
    texto += f"\nTOTAL GERAL: R$ {total_geral:.2f}"

    return texto
