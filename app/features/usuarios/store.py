from __future__ import annotations

import sqlite3
from datetime import datetime
from typing import Optional

from app.config.settings import SQLITE_DB_PATH
from app.domain.models import Usuario


def _norm_email(email: str) -> str:
    return str(email or "").strip().lower()


def _get_conn() -> sqlite3.Connection:
    SQLITE_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(SQLITE_DB_PATH), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def _init_db() -> None:
    with _get_conn() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS usuarios (
                id TEXT PRIMARY KEY,
                nome TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                telefone TEXT NOT NULL,
                senha_hash TEXT NOT NULL,
                criado_em TEXT NOT NULL
            )
            """
        )
        conn.execute("CREATE INDEX IF NOT EXISTS idx_usuarios_email ON usuarios(email)")


_init_db()


def create_user(*, nome: str, email: str, telefone: str, senha_hash: str) -> Usuario:
    email_norm = _norm_email(email)
    if not email_norm or "@" not in email_norm:
        raise ValueError("Email invalido")

    user = Usuario(nome=nome, email=email_norm, telefone=telefone, senha_hash=senha_hash)

    try:
        with _get_conn() as conn:
            conn.execute(
                """
                INSERT INTO usuarios (id, nome, email, telefone, senha_hash, criado_em)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    user.id,
                    user.nome,
                    user.email,
                    user.telefone,
                    user.senha_hash,
                    user.criado_em.isoformat(),
                ),
            )
    except sqlite3.IntegrityError as exc:
        raise ValueError("Email ja cadastrado") from exc

    return user


def get_user_by_email(email: str) -> Optional[Usuario]:
    email_norm = _norm_email(email)
    with _get_conn() as conn:
        row = conn.execute("SELECT * FROM usuarios WHERE email = ? LIMIT 1", (email_norm,)).fetchone()

    if not row:
        return None

    return Usuario(
        id=row["id"],
        nome=row["nome"],
        email=row["email"],
        telefone=row["telefone"],
        senha_hash=row["senha_hash"],
        criado_em=datetime.fromisoformat(row["criado_em"]),
    )


def get_user_by_id(user_id: str) -> Optional[Usuario]:
    with _get_conn() as conn:
        row = conn.execute("SELECT * FROM usuarios WHERE id = ? LIMIT 1", (user_id,)).fetchone()

    if not row:
        return None

    return Usuario(
        id=row["id"],
        nome=row["nome"],
        email=row["email"],
        telefone=row["telefone"],
        senha_hash=row["senha_hash"],
        criado_em=datetime.fromisoformat(row["criado_em"]),
    )
