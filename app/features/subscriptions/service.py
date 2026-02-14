from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.features.subscriptions.models import Subscription


def get_empresa_subscription(db: Session, empresa_id: str) -> Subscription | None:
    stmt = (
        select(Subscription)
        .where(Subscription.empresa_id == empresa_id)
        .order_by(Subscription.started_at.desc())
    )
    return db.scalars(stmt).first()


def require_empresa_subscription(db: Session, empresa_id: str) -> Subscription:
    subscription = get_empresa_subscription(db, empresa_id)
    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assinatura da empresa nao encontrada",
        )
    return subscription


def update_plan(db: Session, subscription: Subscription, plan_id: str) -> Subscription:
    subscription.plan_id = plan_id.upper()
    db.add(subscription)
    db.commit()
    db.refresh(subscription)
    return subscription
