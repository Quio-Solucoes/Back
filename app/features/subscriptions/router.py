from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.db import get_db
from app.features.auth.dependencies import require_roles
from app.features.subscriptions.schemas import SubscriptionResponse, UpdatePlanRequest
from app.features.subscriptions.service import require_empresa_subscription, update_plan
from app.features.users.enums import UserRole
from app.features.users.models import User


router = APIRouter(prefix="/subscriptions", tags=["subscriptions"])


@router.get("/me", response_model=SubscriptionResponse)
def get_my_subscription(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.OWNER, UserRole.ADMIN, UserRole.MEMBER)),
) -> SubscriptionResponse:
    subscription = require_empresa_subscription(db, current_user.empresa_id)
    return SubscriptionResponse.from_model(subscription)


@router.patch("/me/plan", response_model=SubscriptionResponse)
def update_my_plan(
    payload: UpdatePlanRequest,
    db: Session = Depends(get_db),
    owner_user: User = Depends(require_roles(UserRole.OWNER)),
) -> SubscriptionResponse:
    subscription = require_empresa_subscription(db, owner_user.empresa_id)
    updated = update_plan(db, subscription, payload.plan_id)
    return SubscriptionResponse.from_model(updated)
