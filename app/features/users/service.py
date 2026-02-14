from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.features.users.enums import UserRole, UserStatus
from app.features.users.models import User


def find_user_by_email(db: Session, normalized_email: str) -> User | None:
    stmt = (
        select(User)
        .options(selectinload(User.empresa))
        .where(func.lower(User.email) == normalized_email)
    )
    return db.scalars(stmt).first()


def find_user_by_id(db: Session, user_id: str) -> User | None:
    stmt = select(User).options(selectinload(User.empresa)).where(User.id == user_id)
    return db.scalars(stmt).first()


def list_empresa_users(db: Session, empresa_id: str) -> list[User]:
    stmt = (
        select(User)
        .where(User.empresa_id == empresa_id)
        .order_by(User.created_at.desc())
    )
    return list(db.scalars(stmt).all())


def count_active_users_by_role(db: Session, empresa_id: str, role: UserRole) -> int:
    stmt = (
        select(func.count(User.id))
        .where(User.empresa_id == empresa_id)
        .where(User.role == role)
        .where(User.status == UserStatus.ACTIVE)
    )
    return int(db.scalar(stmt) or 0)


def set_last_login_now(db: Session, user: User) -> None:
    user.last_login_at = datetime.now(timezone.utc)
    db.add(user)
    db.commit()


def create_user(
    db: Session,
    empresa_id: str,
    name: str,
    email: str,
    password_hash: str,
    role: UserRole,
    status: UserStatus,
) -> User:
    user = User(
        empresa_id=empresa_id,
        name=name,
        email=email,
        password_hash=password_hash,
        role=role,
        status=status,
        email_verified=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def update_user_status(db: Session, user: User, status: UserStatus) -> User:
    user.status = status
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
