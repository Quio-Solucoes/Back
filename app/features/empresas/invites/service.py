from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.features.empresas.invites import repository
from app.features.empresas.invites.enums import FranchiseInviteStatus, UserInviteStatus
from app.features.empresas.invites.schema import (
    FranchiseInvite,
    UserInvite,
    generate_plain_token,
    hash_token,
)
from app.features.empresas.memberships.enums import MembershipRole


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def create_franchise_invite(db: Session, email: str) -> tuple[FranchiseInvite, str]:
    token = generate_plain_token()
    invite = FranchiseInvite(
        email=email.strip().lower(),
        token_hash=hash_token(token),
        expires_at=FranchiseInvite.build_expiration(),
    )
    db.add(invite)
    db.commit()
    db.refresh(invite)
    return invite, token


def find_franchise_invite_by_token(db: Session, token: str) -> FranchiseInvite | None:
    token_hash = hash_token(token)
    return repository.get_franchise_invite_by_token_hash(db, token_hash)


def list_franchise_invites(db: Session) -> list[FranchiseInvite]:
    return repository.list_franchise_invites(db)


def find_franchise_invite_by_registered_empresa_id(db: Session, empresa_id: str) -> FranchiseInvite | None:
    return repository.get_franchise_invite_by_registered_empresa_id(db, empresa_id)


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
    role: MembershipRole,
) -> tuple[UserInvite, str]:
    normalized_email = email.strip().lower()

    existing_pending = repository.get_pending_user_invite_by_email(
        db,
        empresa_id=empresa_id,
        normalized_email=normalized_email,
    )
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
        expires_at=UserInvite.build_expiration(),
    )
    db.add(invite)
    db.commit()
    db.refresh(invite)
    return invite, token


def find_user_invite_by_token(db: Session, token: str) -> UserInvite | None:
    return repository.get_user_invite_by_token_hash(db, hash_token(token))


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
