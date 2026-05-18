from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from typing import Any, Optional
from uuid import uuid4

from app.config.settings import SQLITE_DB_PATH


def _get_conn() -> sqlite3.Connection:
    SQLITE_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(SQLITE_DB_PATH), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def _iso_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _has_column(conn: sqlite3.Connection, table: str, column: str) -> bool:
    rows = conn.execute(f"PRAGMA table_info({table})").fetchall()
    return any(r["name"] == column for r in rows)


def _init_db() -> None:
    with _get_conn() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS orcamentos (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                nome TEXT NOT NULL,
                cliente TEXT NOT NULL,
                arquiteto TEXT NOT NULL,
                ambiente TEXT,
                status TEXT NOT NULL,
                criado_em TEXT NOT NULL,
                atualizado_em TEXT NOT NULL
            )
            """
        )

        # Migração leve: versões antigas podem ter criado a tabela sem `user_id`.
        if not _has_column(conn, "orcamentos", "user_id"):
            conn.execute("ALTER TABLE orcamentos ADD COLUMN user_id TEXT")

        conn.execute("CREATE INDEX IF NOT EXISTS idx_orcamentos_cliente ON orcamentos(cliente)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_orcamentos_arquiteto ON orcamentos(arquiteto)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_orcamentos_ambiente ON orcamentos(ambiente)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_orcamentos_status ON orcamentos(status)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_orcamentos_user_id ON orcamentos(user_id)")

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS orcamento_itens (
                id TEXT PRIMARY KEY,
                orcamento_id TEXT NOT NULL,
                user_id TEXT NOT NULL,
                vista_id TEXT NOT NULL,
                produto_id INTEGER NOT NULL,
                produto_nome TEXT NOT NULL,
                dimensao TEXT NOT NULL,
                cor TEXT NOT NULL,
                quantidade INTEGER NOT NULL,
                preco_unitario REAL NOT NULL,
                criado_em TEXT NOT NULL,
                atualizado_em TEXT NOT NULL
            )
            """
        )
        conn.execute("CREATE INDEX IF NOT EXISTS idx_orcamento_itens_orcamento_id ON orcamento_itens(orcamento_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_orcamento_itens_user_id ON orcamento_itens(user_id)")


_init_db()


def create_orcamento(*, user_id: str, cliente: str, arquiteto: str, ambiente: Optional[str] = None) -> dict[str, Any]:
    user_id = str(user_id or "").strip()
    cliente = str(cliente or "").strip()
    arquiteto = str(arquiteto or "").strip()
    ambiente_value = str(ambiente or "").strip() or None

    if not user_id:
        raise ValueError("user_id obrigatorio")
    if not cliente:
        raise ValueError("cliente obrigatorio")
    if not arquiteto:
        raise ValueError("arquiteto obrigatorio")

    orcamento_id = str(uuid4())
    nome = f"{cliente} â€¢ {arquiteto}"
    now = _iso_now()

    with _get_conn() as conn:
        conn.execute(
            """
            INSERT INTO orcamentos (id, user_id, nome, cliente, arquiteto, ambiente, status, criado_em, atualizado_em)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (orcamento_id, user_id, nome, cliente, arquiteto, ambiente_value, "draft", now, now),
        )

    return {
        "id": orcamento_id,
        "user_id": user_id,
        "nome": nome,
        "cliente": cliente,
        "arquiteto": arquiteto,
        "ambiente": ambiente_value,
        "status": "draft",
        "criado_em": now,
        "atualizado_em": now,
    }


def list_orcamentos(*, user_id: str) -> list[dict[str, Any]]:
    with _get_conn() as conn:
        rows = conn.execute("SELECT * FROM orcamentos WHERE user_id = ? ORDER BY criado_em DESC", (user_id,)).fetchall()
    return [dict(row) for row in rows]


def get_orcamento(*, orcamento_id: str, user_id: str) -> Optional[dict[str, Any]]:
    with _get_conn() as conn:
        row = conn.execute(
            "SELECT * FROM orcamentos WHERE id = ? AND user_id = ? LIMIT 1",
            (orcamento_id, user_id),
        ).fetchone()
    return dict(row) if row else None


def update_orcamento(
    *,
    orcamento_id: str,
    user_id: str,
    cliente: Optional[str] = None,
    arquiteto: Optional[str] = None,
    ambiente: Optional[str] = None,
    status: Optional[str] = None,
) -> Optional[dict[str, Any]]:
    current = get_orcamento(orcamento_id=orcamento_id, user_id=user_id)
    if not current:
        return None

    next_cliente = str(cliente).strip() if cliente is not None else str(current["cliente"])
    next_arquiteto = str(arquiteto).strip() if arquiteto is not None else str(current["arquiteto"])
    next_ambiente = (str(ambiente).strip() or None) if ambiente is not None else current.get("ambiente")
    next_status = str(status).strip() if status is not None else str(current["status"])

    if not next_cliente:
        raise ValueError("cliente obrigatorio")
    if not next_arquiteto:
        raise ValueError("arquiteto obrigatorio")

    next_nome = f"{next_cliente} â€¢ {next_arquiteto}"
    now = _iso_now()

    with _get_conn() as conn:
        conn.execute(
            """
            UPDATE orcamentos
            SET nome = ?, cliente = ?, arquiteto = ?, ambiente = ?, status = ?, atualizado_em = ?
            WHERE id = ? AND user_id = ?
            """,
            (next_nome, next_cliente, next_arquiteto, next_ambiente, next_status, now, orcamento_id, user_id),
        )

    return get_orcamento(orcamento_id=orcamento_id, user_id=user_id)


def delete_orcamento(*, orcamento_id: str, user_id: str) -> bool:
    with _get_conn() as conn:
        conn.execute("DELETE FROM orcamento_itens WHERE orcamento_id = ? AND user_id = ?", (orcamento_id, user_id))
        cur = conn.execute("DELETE FROM orcamentos WHERE id = ? AND user_id = ?", (orcamento_id, user_id))
        return bool(cur.rowcount)


def create_orcamento_item(
    *,
    orcamento_id: str,
    user_id: str,
    vista_id: str,
    produto_id: int,
    produto_nome: str,
    dimensao: str,
    cor: str,
    quantidade: int,
    preco_unitario: float,
) -> dict[str, Any]:
    orcamento_id = str(orcamento_id or "").strip()
    user_id = str(user_id or "").strip()
    vista_id = str(vista_id or "").strip() or "frontal"
    produto_nome = str(produto_nome or "").strip()
    dimensao = str(dimensao or "").strip()
    cor = str(cor or "").strip()
    quantidade_int = int(quantidade or 0)
    preco = float(preco_unitario or 0.0)

    if not orcamento_id:
        raise ValueError("orcamento_id obrigatorio")
    if not user_id:
        raise ValueError("user_id obrigatorio")
    if not produto_nome:
        raise ValueError("produto_nome obrigatorio")
    if quantidade_int < 1:
        raise ValueError("quantidade invalida")

    item_id = str(uuid4())
    now = _iso_now()

    with _get_conn() as conn:
        conn.execute(
            """
            INSERT INTO orcamento_itens (
                id, orcamento_id, user_id, vista_id,
                produto_id, produto_nome, dimensao, cor,
                quantidade, preco_unitario, criado_em, atualizado_em
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                item_id,
                orcamento_id,
                user_id,
                vista_id,
                int(produto_id),
                produto_nome,
                dimensao,
                cor,
                quantidade_int,
                preco,
                now,
                now,
            ),
        )

    return {
        "id": item_id,
        "orcamento_id": orcamento_id,
        "user_id": user_id,
        "vista_id": vista_id,
        "produto_id": int(produto_id),
        "produto_nome": produto_nome,
        "dimensao": dimensao,
        "cor": cor,
        "quantidade": quantidade_int,
        "preco_unitario": preco,
        "criado_em": now,
        "atualizado_em": now,
    }


def list_orcamento_itens(*, orcamento_id: str, user_id: str) -> list[dict[str, Any]]:
    with _get_conn() as conn:
        rows = conn.execute(
            """
            SELECT *
            FROM orcamento_itens
            WHERE orcamento_id = ? AND user_id = ?
            ORDER BY criado_em ASC, id ASC
            """,
            (orcamento_id, user_id),
        ).fetchall()
    return [dict(r) for r in rows]


def update_orcamento_item(
    *,
    item_id: str,
    user_id: str,
    vista_id: Optional[str] = None,
    produto_id: Optional[int] = None,
    produto_nome: Optional[str] = None,
    dimensao: Optional[str] = None,
    cor: Optional[str] = None,
    quantidade: Optional[int] = None,
    preco_unitario: Optional[float] = None,
) -> bool:
    fields: list[str] = []
    values: list[Any] = []

    if vista_id is not None:
        fields.append("vista_id = ?")
        values.append(str(vista_id or "").strip() or "frontal")
    if produto_id is not None:
        fields.append("produto_id = ?")
        values.append(int(produto_id))
    if produto_nome is not None:
        fields.append("produto_nome = ?")
        values.append(str(produto_nome or "").strip())
    if dimensao is not None:
        fields.append("dimensao = ?")
        values.append(str(dimensao or "").strip())
    if cor is not None:
        fields.append("cor = ?")
        values.append(str(cor or "").strip())
    if quantidade is not None:
        fields.append("quantidade = ?")
        values.append(int(quantidade))
    if preco_unitario is not None:
        fields.append("preco_unitario = ?")
        values.append(float(preco_unitario))

    if not fields:
        return False

    fields.append("atualizado_em = ?")
    values.append(_iso_now())
    values.extend([str(item_id), str(user_id)])

    sql = f"UPDATE orcamento_itens SET {', '.join(fields)} WHERE id = ? AND user_id = ?"
    with _get_conn() as conn:
        cur = conn.execute(sql, tuple(values))
        return bool(cur.rowcount)


def delete_orcamento_item(*, item_id: str, user_id: str) -> bool:
    with _get_conn() as conn:
        cur = conn.execute("DELETE FROM orcamento_itens WHERE id = ? AND user_id = ?", (item_id, user_id))
        return bool(cur.rowcount)
