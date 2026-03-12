from sqlalchemy.orm import Session

from app.features.empresas.repository import get_empresa_by_id
from app.features.identity.repository import get_by_login_identifier
from app.features.invites.repository import get_franchise_invite_by_registered_empresa_id
from app.features.subscriptions.repository import get_latest_subscription_by_empresa_id
from app.features.memberships.enums import MembershipRole
from app.features.users.repository import get_user_by_empresa_and_role
from app.features.users.schema import User


def owner_email_exists(db: Session, normalized_email: str) -> bool:
    return get_by_login_identifier(db, normalized_email) is not None


def get_owner_by_empresa_id(db: Session, empresa_id: str) -> User | None:
    return get_user_by_empresa_and_role(db, empresa_id, MembershipRole.OWNER)


def get_latest_subscription(db: Session, empresa_id: str):
    return get_latest_subscription_by_empresa_id(db, empresa_id)


def get_empresa(db: Session, empresa_id: str):
    return get_empresa_by_id(db, empresa_id)


def get_franchise_invite_by_empresa_id(db: Session, empresa_id: str):
    return get_franchise_invite_by_registered_empresa_id(db, empresa_id)
