from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.features.auth.identity import repository
from app.features.auth.identity.enums import AuthAccountStatus
from app.features.auth.identity.schema import AuthAccount
from app.features.auth.password_service import hash_password


def create_auth_account(
    db: Session,
    user_id: str,
    login_identifier: str,
    password: str,
) -> AuthAccount:
    password_hash, policy_version, pepper_version = hash_password(password)
    account = AuthAccount(
        user_id=user_id,
        login_identifier=login_identifier.strip().lower(),
        password_hash=password_hash,
        hash_policy_version=policy_version,
        pepper_version=pepper_version,
        password_changed_at=datetime.now(timezone.utc),
    )
    db.add(account)
    db.commit()
    db.refresh(account)
    return account


def find_auth_account_by_login_identifier(db: Session, login_identifier: str) -> AuthAccount | None:
    """Fetch auth account together with related user and memberships."""
    return repository.get_by_login_identifier(db, login_identifier.strip().lower())


def find_auth_account_by_user_id(db: Session, user_id: str) -> AuthAccount | None:
    return repository.get_by_user_id(db, user_id)


def register_failed_login_attempt(db: Session, account: AuthAccount) -> None:
    repository.save_failed_attempt(db, account)


def mark_successful_login(db: Session, account: AuthAccount, when: datetime) -> None:
    repository.mark_successful_login(db, account, when)


def set_account_status(db: Session, account: AuthAccount, status: AuthAccountStatus) -> None:
    repository.set_status(db, account, status)
