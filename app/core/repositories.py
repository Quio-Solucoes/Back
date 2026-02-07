from __future__ import annotations

from pathlib import Path

import pandas as pd

from app.core.models import Movel, Componente

ARQUIVO = Path(__file__).resolve().parents[2] / "orcamento_final.xlsx"


def _parse_preco(valor):
    if pd.isna(valor):
        return 0.0

    valor = str(valor).strip()

    if "." in valor and "," in valor:
        valor = valor.replace(".", "").replace(",", ".")
    elif "," in valor:
        valor = valor.replace(",", ".")

    return float(valor)


def buscar_movel_por_nome(nome):
    df = pd.read_excel(ARQUIVO, sheet_name="balcoes")
    df.columns = [c.strip().lower() for c in df.columns]

    for _, r in df.iterrows():
        if nome.lower() in r["nome"].lower():
            return Movel(
                r["id"],
                r["nome"],
                r["tipo"],
                r["material"],
                r["cor"],
                _parse_preco(r["preco_base"]),
                r["l_mm"],
                r["a_mm"],
                r["p_mm"],
                r["area"],
                r["descricao"],
            )
    return None


def buscar_componentes_do_movel(movel_id):
    df = pd.read_excel(ARQUIVO, sheet_name="componentes")
    df.columns = [c.strip().lower() for c in df.columns]

    componentes = []

    for _, r in df[df["balcao_id"] == movel_id].iterrows():
        componentes.append(
            Componente(
                nome=r["nome"],
                categoria_funcional=r["categoria_funcional"],
                quantidade=int(r["quantidade"]),
                preco_unitario=_parse_preco(r["preco_unitario"]),
                material=r.get("material"),
                cor=r.get("cor"),
            )
        )

    return componentes


def buscar_catalogo_componentes():
    df = pd.read_excel(ARQUIVO, sheet_name="catalogo_componentes")
    df.columns = [c.strip().lower() for c in df.columns]

    catalogo = {}

    for _, r in df.iterrows():
        cat = r["categoria_funcional"]

        catalogo.setdefault(cat, []).append(
            {
                "id": r["id"],
                "nome": r["nome"],
                "preco_unitario": _parse_preco(r["preco_unitario"]),
            }
        )

    return catalogo

