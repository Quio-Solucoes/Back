from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.features.invites.enums import UserInviteStatus
from app.features.invites.schema import FranchiseInvite, UserInvite


def get_franchise_invite_by_token_hash(db: Session, token_hash: str) -> FranchiseInvite | None:
    stmt = select(FranchiseInvite).where(FranchiseInvite.token_hash == token_hash)
    return db.scalars(stmt).first()


def list_franchise_invites(db: Session) -> list[FranchiseInvite]:
    stmt = select(FranchiseInvite).order_by(FranchiseInvite.created_at.desc())
    return list(db.scalars(stmt).all())


def get_user_invite_by_token_hash(db: Session, token_hash: str) -> UserInvite | None:
    stmt = select(UserInvite).where(UserInvite.token_hash == token_hash)
    return db.scalars(stmt).first()


def get_pending_user_invite_by_email(db: Session, *, empresa_id: str, normalized_email: str) -> UserInvite | None:
    stmt = (
        select(UserInvite)
        .where(UserInvite.empresa_id == empresa_id)
        .where(func.lower(UserInvite.email) == normalized_email)
        .where(UserInvite.status == UserInviteStatus.PENDING)
    )
    return db.scalars(stmt).first()


def get_franchise_invite_by_registered_empresa_id(db: Session, empresa_id: str) -> FranchiseInvite | None:
    stmt = select(FranchiseInvite).where(FranchiseInvite.registered_empresa_id == empresa_id)
    return db.scalars(stmt).first()
