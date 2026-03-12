from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.features.auth.password_service import hash_password
from app.features.auth.identity.schema import AuthAccount


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
