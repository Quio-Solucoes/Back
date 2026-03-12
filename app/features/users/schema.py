from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import CheckConstraint, DateTime, Enum, String
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates

from app.db.db import Base
from app.features.users.enums import UserStatus


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"
    __table_args__ = (
        CheckConstraint(
            "primary_email IS NULL OR primary_email = lower(primary_email)",
            name="ck_users_primary_email_lower",
        ),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    primary_email: Mapped[str | None] = mapped_column(String(255), unique=True, nullable=True, index=True)
    phone: Mapped[str | None] = mapped_column(String(30), nullable=True)
    status: Mapped[UserStatus] = mapped_column(
        Enum(UserStatus, name="user_status"), default=UserStatus.PENDING, nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False
    )

    auth_account = relationship("AuthAccount", back_populates="user", uselist=False)
    memberships = relationship("Membership", back_populates="user", cascade="all, delete-orphan")
    address_links = relationship("UserAddressLink", back_populates="user", cascade="all, delete-orphan")
    addresses = relationship("Address", secondary="user_addresses", back_populates="users", viewonly=True)
    phones = relationship("Phone", back_populates="user", cascade="all, delete-orphan")

    @validates("primary_email")
    def normalize_email(self, key: str, email: str | None) -> str | None:
        del key
        return email.strip().lower() if email else None

    @property
    def default_membership(self):
        if not self.memberships:
            return None
        default = next((m for m in self.memberships if m.is_default), None)
        return default or self.memberships[0]

    @property
    def empresa_id(self) -> str | None:
        membership = self.default_membership
        return membership.empresa_id if membership else None

    @property
    def role(self):
        membership = self.default_membership
        return membership.role if membership else None
