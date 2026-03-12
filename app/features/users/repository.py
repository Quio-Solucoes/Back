from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload, selectinload

from app.features.empresas.memberships.enums import MembershipRole, MembershipStatus
from app.features.empresas.memberships.schema import Membership
from app.features.users.enums import UserStatus
from app.features.users.schema import User


def get_user_by_email(db: Session, normalized_email: str) -> User | None:
    stmt = (
        select(User)
        .options(
            selectinload(User.memberships).selectinload(Membership.empresa),
        )
        .where(func.lower(User.primary_email) == normalized_email)
    )
    return db.scalars(stmt).first()


def get_user_by_id(db: Session, user_id: str) -> User | None:
    stmt = (
        select(User)
        .options(
            selectinload(User.memberships).selectinload(Membership.empresa),
        )
        .where(User.id == user_id)
    )
    return db.scalars(stmt).first()


def list_users_by_empresa(db: Session, empresa_id: str) -> list[User]:
    stmt = (
        select(User)
        .join(Membership, Membership.user_id == User.id)
        .options(
            joinedload(User.memberships).joinedload(Membership.empresa),
        )
        .where(Membership.empresa_id == empresa_id)
        .where(Membership.status == MembershipStatus.ACTIVE)
        .order_by(User.created_at.desc())
    )
    return list(db.scalars(stmt).unique().all())


def get_user_by_empresa_and_role(db: Session, empresa_id: str, role: MembershipRole) -> User | None:
    stmt = (
        select(User)
        .join(Membership, Membership.user_id == User.id)
        .where(Membership.empresa_id == empresa_id)
        .where(Membership.role == role)
        .where(Membership.status == MembershipStatus.ACTIVE)
    )
    return db.scalars(stmt).first()


def count_active_users_by_role(db: Session, empresa_id: str, role: MembershipRole) -> int:
    stmt = (
        select(func.count(User.id))
        .join(Membership, Membership.user_id == User.id)
        .where(Membership.empresa_id == empresa_id)
        .where(Membership.role == role)
        .where(Membership.status == MembershipStatus.ACTIVE)
    )
    return int(db.scalar(stmt) or 0)


def count_active_users_by_roles(db: Session, empresa_id: str, roles: list[MembershipRole]) -> int:
    stmt = (
        select(func.count(User.id))
        .join(Membership, Membership.user_id == User.id)
        .where(Membership.empresa_id == empresa_id)
        .where(Membership.role.in_(roles))
        .where(Membership.status == MembershipStatus.ACTIVE)
    )
    return int(db.scalar(stmt) or 0)


def user_email_exists(db: Session, normalized_email: str) -> bool:
    stmt = select(User.id).where(func.lower(User.primary_email) == normalized_email)
    return db.scalar(stmt) is not None
