from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.features.auth.identity.enums import AuthAccountStatus
from app.features.auth.identity.schema import AuthAccount
from app.features.empresas.memberships.schema import Membership
from app.features.users.schema import User


def get_by_login_identifier(db: Session, login_identifier: str) -> AuthAccount | None:
    stmt = (
        select(AuthAccount)
        .options(
            selectinload(AuthAccount.user)
            .selectinload(User.memberships)
            .selectinload(Membership.empresa)
        )
        .where(AuthAccount.login_identifier == login_identifier)
    )
    return db.scalars(stmt).first()


def get_by_user_id(db: Session, user_id: str) -> AuthAccount | None:
    stmt = select(AuthAccount).where(AuthAccount.user_id == user_id)
    return db.scalars(stmt).first()


def save_failed_attempt(db: Session, account: AuthAccount) -> None:
    account.failed_login_attempts += 1
    db.add(account)
    db.commit()


def mark_successful_login(db: Session, account: AuthAccount, when: datetime) -> None:
    account.failed_login_attempts = 0
    account.last_login_at = when
    db.add(account)
    db.commit()


def set_status(db: Session, account: AuthAccount, status: AuthAccountStatus) -> None:
    account.status = status
    db.add(account)
    db.commit()
