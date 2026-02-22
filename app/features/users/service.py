from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.features.users import repository
from app.features.users.enums import UserRole, UserStatus
from app.features.users.schema import User


def find_user_by_email(db: Session, normalized_email: str) -> User | None:
    return repository.get_user_by_email(db, normalized_email)


def find_user_by_id(db: Session, user_id: str) -> User | None:
    return repository.get_user_by_id(db, user_id)


def list_empresa_users(db: Session, empresa_id: str) -> list[User]:
    return repository.list_users_by_empresa(db, empresa_id)


def count_active_users_by_role(db: Session, empresa_id: str, role: UserRole) -> int:
    return repository.count_active_users_by_role(db, empresa_id, role)


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
