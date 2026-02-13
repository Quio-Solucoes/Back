from pathlib import Path

import pandas as pd

from app.config.settings import EXCEL_FILE
from app.features.ambientes.componentes.model import Componente
from app.features.ambientes.moveis.model import Movel
from app.features.chat.helpers_tabbles import normalizar


def _parse_preco(valor) -> float:
    if pd.isna(valor):
        return 0.0

    valor = str(valor).strip()

    if "." in valor and "," in valor:
        valor = valor.replace(".", "").replace(",", ".")
    elif "," in valor:
        valor = valor.replace(",", ".")

    return float(valor)


def _load_sheet(sheet_name: str) -> pd.DataFrame:
    excel_path = Path(EXCEL_FILE)
    if not excel_path.exists():
        raise FileNotFoundError(f"Arquivo de catalogo nao encontrado: {excel_path}")
    df = pd.read_excel(excel_path, sheet_name=sheet_name)
    df.columns = [c.strip().lower() for c in df.columns]
    return df


def buscar_movel_por_nome(nome: str):
    df = _load_sheet("balcoes")

    for _, r in df.iterrows():
        if nome.lower() in str(r["nome"]).lower():
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


def buscar_componentes_do_movel(movel_id: int) -> list[Componente]:
    df = _load_sheet("componentes")

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


def buscar_catalogo_componentes() -> dict[str, list[dict]]:
    df = _load_sheet("catalogo_componentes")

    catalogo = {}
    for _, r in df.iterrows():
        categoria = normalizar(str(r["categoria_funcional"]))
        catalogo.setdefault(categoria, []).append(
            {
                "id": str(r["id"]),
                "nome": r["nome"],
                "preco_unitario": _parse_preco(r["preco_unitario"]),
            }
        )

    return catalogo
