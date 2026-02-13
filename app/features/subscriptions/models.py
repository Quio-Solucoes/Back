from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import DateTime, Enum, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.db import Base
from app.features.subscriptions.enums import BillingCycle, SubscriptionStatus


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Subscription(Base):
    __tablename__ = "subscriptions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    empresa_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("empresas.id", ondelete="CASCADE"),
        nullable=False,
    )
    plan_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    status: Mapped[SubscriptionStatus] = mapped_column(
        Enum(SubscriptionStatus, name="subscription_status"),
        default=SubscriptionStatus.ACTIVE,
        nullable=False,
    )
    billing_cycle: Mapped[BillingCycle] = mapped_column(
        Enum(BillingCycle, name="billing_cycle"),
        default=BillingCycle.MONTHLY,
        nullable=False,
    )
    current_price: Mapped[float] = mapped_column(Numeric(10, 2), default=0, nullable=False)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)
    current_period_end: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    canceled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    empresa = relationship("Empresa", back_populates="subscriptions")
