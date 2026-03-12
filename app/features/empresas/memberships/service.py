from sqlalchemy.orm import Session

from app.features.empresas.memberships.enums import MembershipRole, MembershipStatus
from app.features.empresas.memberships.schema import Membership


def create_membership(
    db: Session,
    user_id: str,
    empresa_id: str,
    role: MembershipRole,
    status: MembershipStatus = MembershipStatus.ACTIVE,
    is_default: bool = False,
    invited_by: str | None = None,
) -> Membership:
    membership = Membership(
        user_id=user_id,
        empresa_id=empresa_id,
        role=role,
        status=status,
        is_default=is_default,
        invited_by=invited_by,
    )
    if is_default:
        _unset_existing_default(db, user_id)
    db.add(membership)
    db.commit()
    db.refresh(membership)
    return membership


def _unset_existing_default(db: Session, user_id: str) -> None:
    db.query(Membership).filter(Membership.user_id == user_id, Membership.is_default.is_(True)).update(
        {"is_default": False}
    )


def set_default_membership(db: Session, membership: Membership) -> Membership:
    _unset_existing_default(db, membership.user_id)
    membership.is_default = True
    db.add(membership)
    db.commit()
    db.refresh(membership)
    return membership
