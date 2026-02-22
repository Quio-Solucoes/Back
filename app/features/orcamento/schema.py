from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.db import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Orcamento(Base):
    __tablename__ = "orcamentos"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    session_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="FINALIZADO")
    total: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    quantidade_moveis: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    pdf_filename: Mapped[str | None] = mapped_column(String(255), nullable=True)
    observacoes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False
    )

    itens = relationship("OrcamentoItem", back_populates="orcamento", cascade="all, delete-orphan")


class OrcamentoItem(Base):
    __tablename__ = "orcamento_itens"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    orcamento_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("orcamentos.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    ordem: Mapped[int] = mapped_column(Integer, nullable=False)
    nome_movel: Mapped[str] = mapped_column(String(255), nullable=False)
    material: Mapped[str | None] = mapped_column(String(100), nullable=True)
    cor: Mapped[str | None] = mapped_column(String(100), nullable=True)
    largura_mm: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    altura_mm: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    profundidade_mm: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    preco_movel: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    total_componentes: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    total_item: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)

    orcamento = relationship("Orcamento", back_populates="itens")
    componentes = relationship(
        "OrcamentoItemComponente",
        back_populates="item",
        cascade="all, delete-orphan",
    )


class OrcamentoItemComponente(Base):
    __tablename__ = "orcamento_item_componentes"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    item_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("orcamento_itens.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    ordem: Mapped[int] = mapped_column(Integer, nullable=False)
    nome: Mapped[str] = mapped_column(String(255), nullable=False)
    categoria_funcional: Mapped[str] = mapped_column(String(100), nullable=False)
    quantidade: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    preco_unitario: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    subtotal: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    material: Mapped[str | None] = mapped_column(String(100), nullable=True)
    cor: Mapped[str | None] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)

    item = relationship("OrcamentoItem", back_populates="componentes")
