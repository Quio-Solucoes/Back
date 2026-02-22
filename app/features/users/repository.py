from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.features.users.enums import UserRole, UserStatus
from app.features.users.schema import User


def get_user_by_email(db: Session, normalized_email: str) -> User | None:
    stmt = (
        select(User)
        .options(selectinload(User.empresa))
        .where(func.lower(User.email) == normalized_email)
    )
    return db.scalars(stmt).first()


def get_user_by_id(db: Session, user_id: str) -> User | None:
    stmt = select(User).options(selectinload(User.empresa)).where(User.id == user_id)
    return db.scalars(stmt).first()


def list_users_by_empresa(db: Session, empresa_id: str) -> list[User]:
    stmt = select(User).where(User.empresa_id == empresa_id).order_by(User.created_at.desc())
    return list(db.scalars(stmt).all())


def get_user_by_empresa_and_role(db: Session, empresa_id: str, role: UserRole) -> User | None:
    stmt = select(User).where(User.empresa_id == empresa_id).where(User.role == role)
    return db.scalars(stmt).first()


def count_active_users_by_role(db: Session, empresa_id: str, role: UserRole) -> int:
    stmt = (
        select(func.count(User.id))
        .where(User.empresa_id == empresa_id)
        .where(User.role == role)
        .where(User.status == UserStatus.ACTIVE)
    )
    return int(db.scalar(stmt) or 0)


def user_email_exists(db: Session, normalized_email: str) -> bool:
    stmt = select(User.id).where(func.lower(User.email) == normalized_email)
    return db.scalar(stmt) is not None
