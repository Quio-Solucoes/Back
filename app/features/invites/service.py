from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.features.invites.enums import FranchiseInviteStatus, UserInviteStatus
from app.features.invites.models import (
    FranchiseInvite,
    UserInvite,
    generate_plain_token,
    hash_token,
)
from app.features.users.enums import UserRole


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def create_franchise_invite(db: Session, email: str, expires_in_days: int) -> tuple[FranchiseInvite, str]:
    token = generate_plain_token()
    invite = FranchiseInvite(
        email=email.strip().lower(),
        token_hash=hash_token(token),
        expires_at=FranchiseInvite.build_expiration(expires_in_days),
    )
    db.add(invite)
    db.commit()
    db.refresh(invite)
    return invite, token


def find_franchise_invite_by_token(db: Session, token: str) -> FranchiseInvite | None:
    token_hash = hash_token(token)
    stmt = select(FranchiseInvite).where(FranchiseInvite.token_hash == token_hash)
    return db.scalars(stmt).first()


def list_franchise_invites(db: Session) -> list[FranchiseInvite]:
    stmt = select(FranchiseInvite).order_by(FranchiseInvite.created_at.desc())
    return list(db.scalars(stmt).all())


def assert_invite_available(invite: FranchiseInvite) -> None:
    if invite.status not in {FranchiseInviteStatus.PENDING}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Convite de franquia indisponivel",
        )
    if invite.expires_at < utcnow():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Convite de franquia expirado",
        )


def create_user_invite(
    db: Session,
    empresa_id: str,
    invited_by_user_id: str,
    email: str,
    role: UserRole,
    expires_in_days: int,
) -> tuple[UserInvite, str]:
    normalized_email = email.strip().lower()

    existing_pending_stmt = (
        select(UserInvite)
        .where(UserInvite.empresa_id == empresa_id)
        .where(func.lower(UserInvite.email) == normalized_email)
        .where(UserInvite.status == UserInviteStatus.PENDING)
    )
    existing_pending = db.scalars(existing_pending_stmt).first()
    if existing_pending:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ja existe convite pendente para este email",
        )

    token = generate_plain_token()
    invite = UserInvite(
        empresa_id=empresa_id,
        invited_by_user_id=invited_by_user_id,
        email=normalized_email,
        role=role,
        token_hash=hash_token(token),
        expires_at=UserInvite.build_expiration(expires_in_days),
    )
    db.add(invite)
    db.commit()
    db.refresh(invite)
    return invite, token


def find_user_invite_by_token(db: Session, token: str) -> UserInvite | None:
    stmt = select(UserInvite).where(UserInvite.token_hash == hash_token(token))
    return db.scalars(stmt).first()


def assert_user_invite_available(invite: UserInvite) -> None:
    if invite.status != UserInviteStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Convite de usuario indisponivel",
        )
    if invite.expires_at < utcnow():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Convite de usuario expirado",
        )
