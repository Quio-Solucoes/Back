from pathlib import Path
from typing import Any
from functools import lru_cache
from urllib.parse import quote

import pandas as pd

from app.config.settings import EXCEL_TESTE_FILE, FOTOS_DIR, PUBLIC_BASE_URL
from app.domain.models import ItemOrcamento, ProdutoCatalogo, VarianteProduto
from app.features.chat.helpers_tabbles import normalizar


def _parse_preco(valor: Any) -> float:
    if pd.isna(valor):
        return 0.0

    texto = str(valor).strip()
    if "." in texto and "," in texto:
        texto = texto.replace(".", "").replace(",", ".")
    elif "," in texto:
        texto = texto.replace(",", ".")
    return float(texto or 0.0)


def _excel_path() -> Path:
    path = Path(EXCEL_TESTE_FILE)
    if not path.exists():
        raise FileNotFoundError(f"Arquivo de catalogo de teste nao encontrado: {path}")
    return path


def _load_sheet(sheet_name: str) -> pd.DataFrame:
    df = pd.read_excel(_excel_path(), sheet_name=sheet_name)
    df.columns = [str(c).strip().lower() for c in df.columns]
    return df


def _get_col(row: pd.Series, *keys: str, default: Any = "") -> Any:
    for k in keys:
        if k in row and not pd.isna(row[k]):
            return row[k]
    return default


@lru_cache(maxsize=1)
def _index_fotos() -> dict[str, str]:
    index: dict[str, str] = {}
    if not FOTOS_DIR.exists():
        return index

    for p in FOTOS_DIR.iterdir():
        if not p.is_file():
            continue
        index[normalizar(p.stem)] = p.name

    return index


def _imagem_url(value: Any) -> str:
    raw = str(value or "").strip()
    if not raw:
        return ""

    filename = _index_fotos().get(normalizar(Path(raw).stem))
    if not filename:
        return ""

    path = f"/fotos/{quote(filename)}"
    if PUBLIC_BASE_URL:
        return f"{PUBLIC_BASE_URL}{path}"
    return path


def _normalizar_dimensao(value: str) -> str:
    raw = str(value or "").strip().lower()
    raw = raw.replace("mm", "").replace(" ", "")
    raw = raw.replace("×", "x").replace("*", "x")
    parts = [p for p in raw.split("x") if p]
    if len(parts) < 2:
        return normalizar(raw)
    return "x".join(parts)


def buscar_produtos_por_termo(termo: str) -> list[dict]:
    termo = str(termo or "").strip()
    if not termo or len(termo) < 2:
        return []

    df = _load_sheet("produto")
    termo_norm = normalizar(termo)

    resultados: list[dict] = []
    for _, r in df.iterrows():
        nome = str(r.get("nome", "")).strip()
        if not nome:
            continue

        if termo_norm not in normalizar(nome):
            continue

        descricao = _get_col(r, "descrição", "descricao", "descriÃ§Ã£o", default="")
        imagem = _get_col(r, "imagem", default="")

        resultados.append(
            {
                "id": int(r.get("id")),
                "nome": nome,
                "descricao": str(descricao or ""),
                "imagem": _imagem_url(imagem),
            }
        )

    return resultados


def buscar_variantes_produto(produto_id: int) -> dict | None:
    df = _load_sheet("possibilidades")
    df_prod = df[df["id"] == int(produto_id)]
    if df_prod.empty:
        return None

    dimensoes: list[str] = []
    cores: list[str] = []

    for _, r in df_prod.iterrows():
        dim = str(r.get("dimensao", "")).strip()
        cor = str(r.get("cor", "")).strip()
        if dim and dim not in dimensoes:
            dimensoes.append(dim)
        if cor and cor not in cores:
            cores.append(cor)

    return {"dimensoes": sorted(dimensoes), "cores": sorted(cores)}


def criar_item_por_etapas(produto_id: int, dimensao: str, cor: str, quantidade: int) -> dict:
    df_prod = _load_sheet("produto")
    produto_row = df_prod[df_prod["id"] == int(produto_id)]
    if produto_row.empty:
        return {"error": f"Produto {produto_id} nao encontrado"}

    r = produto_row.iloc[0]
    nome = str(r.get("nome", "")).strip()
    descricao = _get_col(r, "descrição", "descricao", "descriÃ§Ã£o", default="")
    imagem = _get_col(r, "imagem", default="")

    produto = ProdutoCatalogo(
        id=int(r.get("id")),
        nome=nome,
        descricao=str(descricao or ""),
        imagem=_imagem_url(imagem),
    )

    df_poss = _load_sheet("possibilidades")
    df_poss = df_poss[df_poss["id"] == int(produto_id)]

    dimensao_norm = _normalizar_dimensao(dimensao)
    cor_norm = normalizar(cor)

    variante: VarianteProduto | None = None
    for _, vr in df_poss.iterrows():
        dim_planilha = _normalizar_dimensao(str(vr.get("dimensao", "")))
        cor_planilha = normalizar(str(vr.get("cor", "")))
        if dim_planilha == dimensao_norm and cor_planilha == cor_norm:
            variante = VarianteProduto(
                produto_id=int(vr.get("id")),
                dimensao=str(vr.get("dimensao", dimensao)).strip(),
                cor=str(vr.get("cor", cor)).strip(),
                preco=_parse_preco(_get_col(vr, "preço", "preco", "preÃ§o", default=0)),
            )
            break

    if variante is None and not df_poss.empty:
        vr = df_poss.iloc[0]
        variante = VarianteProduto(
            produto_id=int(vr.get("id")),
            dimensao=str(vr.get("dimensao", dimensao)).strip(),
            cor=str(vr.get("cor", cor)).strip(),
            preco=_parse_preco(_get_col(vr, "preço", "preco", "preÃ§o", default=0)),
        )

    if variante is None:
        return {"error": f"Variante nao encontrada: {dimensao} / {cor}"}

    item = ItemOrcamento(produto=produto, variante=variante, quantidade=int(quantidade or 1))
    return {"item_obj": item}
