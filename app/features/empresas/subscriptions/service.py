from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.features.empresas.subscriptions import repository
from app.features.empresas.subscriptions.schema import Subscription


def get_empresa_subscription(db: Session, empresa_id: str) -> Subscription | None:
    return repository.get_latest_subscription_by_empresa_id(db, empresa_id)


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
