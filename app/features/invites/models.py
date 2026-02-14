import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from sqlalchemy import DateTime, Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.db import Base
from app.features.invites.enums import FranchiseInviteStatus, UserInviteStatus
from app.features.users.enums import UserRole


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def generate_plain_token() -> str:
    return secrets.token_urlsafe(32)


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


class FranchiseInvite(Base):
    __tablename__ = "franchise_invites"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    email: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    token_hash: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    status: Mapped[FranchiseInviteStatus] = mapped_column(
        Enum(FranchiseInviteStatus, name="franchise_invite_status"),
        default=FranchiseInviteStatus.PENDING,
        nullable=False,
    )
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    registered_empresa_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("empresas.id", ondelete="SET NULL"),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)

    empresa = relationship("Empresa")

    @staticmethod
    def build_expiration(days: int = 7) -> datetime:
        return utcnow() + timedelta(days=days)


class UserInvite(Base):
    __tablename__ = "user_invites"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    empresa_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("empresas.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    invited_by_user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    email: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole, name="user_invite_role"), nullable=False)
    token_hash: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    status: Mapped[UserInviteStatus] = mapped_column(
        Enum(UserInviteStatus, name="user_invite_status"),
        default=UserInviteStatus.PENDING,
        nullable=False,
    )
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    accepted_user_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)

    empresa = relationship("Empresa")
    invited_by = relationship("User", foreign_keys=[invited_by_user_id])
    accepted_user = relationship("User", foreign_keys=[accepted_user_id])

    @staticmethod
    def build_expiration(days: int = 7) -> datetime:
        return utcnow() + timedelta(days=days)
