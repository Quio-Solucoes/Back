from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import Boolean, CheckConstraint, DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.db import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Phone(Base):
    __tablename__ = "phones"
    __table_args__ = (
        CheckConstraint(
            "(empresa_id IS NOT NULL AND user_id IS NULL) OR (empresa_id IS NULL AND user_id IS NOT NULL)",
            name="ck_phones_single_owner",
        ),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    empresa_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("empresas.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    user_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    label: Mapped[str | None] = mapped_column(String(30), nullable=True)
    phone_number: Mapped[str] = mapped_column(String(20), nullable=False)
    is_whatsapp: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_primary: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False
    )

    empresa = relationship("Empresa", back_populates="phones")
    user = relationship("User", back_populates="phones")
