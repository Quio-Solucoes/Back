from sqlalchemy.orm import Session

from app.features.users import repository
from app.features.empresas.memberships.enums import MembershipRole
from app.features.users.enums import UserStatus
from app.features.users.schema import User


def find_user_by_email(db: Session, normalized_email: str) -> User | None:
    return repository.get_user_by_email(db, normalized_email)


def find_user_by_id(db: Session, user_id: str) -> User | None:
    return repository.get_user_by_id(db, user_id)


def list_empresa_users(db: Session, empresa_id: str) -> list[User]:
    return repository.list_users_by_empresa(db, empresa_id)


def count_active_users_by_role(db: Session, empresa_id: str, role) -> int:
    return repository.count_active_users_by_role(db, empresa_id, role)


def count_active_users_by_roles(db: Session, empresa_id: str, roles: list[MembershipRole]) -> int:
    return repository.count_active_users_by_roles(db, empresa_id, roles)


def find_user_by_empresa_and_role(db: Session, empresa_id: str, role: MembershipRole) -> User | None:
    return repository.get_user_by_empresa_and_role(db, empresa_id, role)


def user_email_exists(db: Session, normalized_email: str) -> bool:
    return repository.user_email_exists(db, normalized_email.strip().lower())


def create_user(
    db: Session,
    name: str,
    primary_email: str | None,
    status: UserStatus,
) -> User:
    user = User(
        name=name,
        primary_email=primary_email,
        status=status,
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
