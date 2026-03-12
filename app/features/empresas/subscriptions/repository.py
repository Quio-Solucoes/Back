from sqlalchemy import select
from sqlalchemy.orm import Session

from app.features.subscriptions.schema import Subscription


def get_latest_subscription_by_empresa_id(db: Session, empresa_id: str) -> Subscription | None:
    stmt = (
        select(Subscription)
        .where(Subscription.empresa_id == empresa_id)
        .order_by(Subscription.started_at.desc())
    )
    return db.scalars(stmt).first()
