from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.features.empresas.memberships.enums import MembershipRole, MembershipStatus
from app.features.empresas.memberships.schema import Membership


def list_by_empresa(db: Session, empresa_id: str) -> list[Membership]:
    stmt = (
        select(Membership)
        .options(selectinload(Membership.user))
        .where(Membership.empresa_id == empresa_id)
        .where(Membership.status == MembershipStatus.ACTIVE)
    )
    return list(db.scalars(stmt).all())


def count_active_by_role(db: Session, empresa_id: str, role: MembershipRole) -> int:
    stmt = (
        select(Membership)
        .where(Membership.empresa_id == empresa_id)
        .where(Membership.role == role)
        .where(Membership.status == MembershipStatus.ACTIVE)
    )
    return len(list(db.scalars(stmt).all()))


def count_active_by_roles(db: Session, empresa_id: str, roles: list[MembershipRole]) -> int:
    stmt = (
        select(Membership)
        .where(Membership.empresa_id == empresa_id)
        .where(Membership.role.in_(roles))
        .where(Membership.status == MembershipStatus.ACTIVE)
    )
    return len(list(db.scalars(stmt).all()))


def get_default_for_user(db: Session, user_id: str) -> Membership | None:
    stmt = select(Membership).where(Membership.user_id == user_id).order_by(Membership.is_default.desc())
    return db.scalars(stmt).first()


def get_by_user_and_empresa(db: Session, user_id: str, empresa_id: str) -> Membership | None:
    stmt = select(Membership).where(Membership.user_id == user_id).where(Membership.empresa_id == empresa_id)
    return db.scalars(stmt).first()
