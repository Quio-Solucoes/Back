from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import Boolean, CheckConstraint, DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates

from app.db.db import Base
from app.features.auth.identity.enums import AuthAccountStatus


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class AuthAccount(Base):
    __tablename__ = "auth_accounts"
    __table_args__ = (
        CheckConstraint("login_identifier = lower(login_identifier)", name="ck_auth_accounts_login_lower"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    login_identifier: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    hash_policy_version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    pepper_version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    email_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    mfa_enabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    failed_login_attempts: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    locked_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    password_changed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_rehash_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[AuthAccountStatus] = mapped_column(
        Enum(AuthAccountStatus, name="auth_account_status"),
        default=AuthAccountStatus.ACTIVE,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False
    )

    user = relationship("User", back_populates="auth_account")

    @validates("login_identifier")
    def normalize_login_identifier(self, key: str, value: str) -> str:
        del key
        return value.strip().lower()
