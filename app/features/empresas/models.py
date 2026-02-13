from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import DateTime, Enum, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.features.empresas.enums import EmpresaStatus
from app.db.db import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Empresa(Base):
    __tablename__ = "empresas"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    razao_social: Mapped[str] = mapped_column(String(255), nullable=False)
    nome_fantasia: Mapped[str | None] = mapped_column(String(255), nullable=True)
    cnpj: Mapped[str | None] = mapped_column(String(18), unique=True, nullable=True)
    status: Mapped[EmpresaStatus] = mapped_column(
        Enum(EmpresaStatus, name="empresa_status"),
        default=EmpresaStatus.ACTIVE,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False
    )

    users = relationship("User", back_populates="empresa", cascade="all, delete-orphan")
    subscriptions = relationship("Subscription", back_populates="empresa", cascade="all, delete-orphan")
