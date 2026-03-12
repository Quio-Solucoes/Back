from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.features.auth.dtos import (
    AuthenticatedIdentity,
    LoginRequest,
    LoginResponse,
    MembershipClaim,
)
from app.features.auth.password_service import needs_rehash, rehash_password, verify_password
from app.features.auth.security import create_access_token
from app.features.empresas.enums import EmpresaStatus
from app.features.auth.identity.enums import AuthAccountStatus
from app.features.auth.identity.repository import (
    get_by_login_identifier,
    mark_successful_login,
    save_failed_attempt,
)
from app.features.auth.identity.schema import AuthAccount
from app.features.empresas.memberships.enums import MembershipStatus
from app.features.users.enums import UserStatus

MAX_FAILED_ATTEMPTS = 5
LOCK_WINDOW_MINUTES = 15


def login(db: Session, payload: LoginRequest) -> LoginResponse:
    account = get_by_login_identifier(db=db, login_identifier=payload.login_identifier)

    invalid_credentials = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciais invalidas",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if not account or not account.user:
        raise invalid_credentials

    now = datetime.now(timezone.utc)
    _assert_account_active(account, now)

    if not verify_password(account, payload.password):
        _register_failure(db, account, now)
        raise invalid_credentials

    _after_successful_auth(db, account, payload.password, now)

    user = account.user
    if user.status != UserStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario inativo ou suspenso",
        )

    active_memberships = [
        m for m in user.memberships if m.status == MembershipStatus.ACTIVE and m.empresa.status == EmpresaStatus.ACTIVE
    ]
    if not active_memberships:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario sem memberships ativas",
        )

    identity_memberships = [
        MembershipClaim(
            membership_id=m.id,
            empresa_id=m.empresa_id,
            role=m.role.value,
            is_default=m.is_default,
        )
        for m in active_memberships
    ]

    default_membership = next((m for m in active_memberships if m.is_default), active_memberships[0])
    token = create_access_token(
        {
            "sub": account.id,
            "user_id": user.id,
            "membership_id": default_membership.id,
            "empresa_id": default_membership.empresa_id,
            "tenant_id": default_membership.empresa_id,
            "role": default_membership.role.value,
        }
    )
    identity = AuthenticatedIdentity(
        auth_account_id=account.id,
        user_id=user.id,
        memberships=identity_memberships,
    )
    return LoginResponse(access_token=token, identity=identity)


def _assert_account_active(account: AuthAccount, now: datetime) -> None:
    if account.status == AuthAccountStatus.DISABLED:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Conta desativada",
        )
    if account.locked_until and account.locked_until > now:
        raise HTTPException(
            status_code=status.HTTP_423_LOCKED,
            detail="Conta bloqueada temporariamente",
        )


def _register_failure(db: Session, account: AuthAccount, now: datetime) -> None:
    save_failed_attempt(db, account)
    if account.failed_login_attempts >= MAX_FAILED_ATTEMPTS:
        account.locked_until = now + timedelta(minutes=LOCK_WINDOW_MINUTES)
        account.status = AuthAccountStatus.LOCKED
        db.add(account)
        db.commit()


def _after_successful_auth(db: Session, account: AuthAccount, password: str, now: datetime) -> None:
    if needs_rehash(account):
        rehash_password(account, password)
    account.failed_login_attempts = 0
    account.locked_until = None
    account.status = AuthAccountStatus.ACTIVE
    account.last_login_at = now
    db.add(account)
    db.commit()
