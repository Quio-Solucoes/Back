from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.db import get_db
from app.features.auth.dependencies import get_current_user, require_roles
from app.features.auth.security import hash_password
from app.features.invites.enums import UserInviteStatus
from app.features.invites.service import (
    assert_user_invite_available,
    create_user_invite,
    find_user_invite_by_token,
)
from app.features.subscriptions.plans import get_plan_limit
from app.features.subscriptions.service import require_empresa_subscription
from app.features.users.enums import UserRole, UserStatus
from app.features.users.schemas import (
    AcceptUserInviteRequest,
    CreateUserInviteRequest,
    UpdateUserStatusRequest,
    UserInviteResponse,
    UserResponse,
)
from app.features.users.service import (
    count_active_users_by_role,
    create_user,
    find_user_by_email,
    find_user_by_id,
    list_empresa_users,
    update_user_status,
)
from app.features.users.models import User


router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserResponse)
def me(current_user: User = Depends(get_current_user)) -> UserResponse:
    return UserResponse.from_model(current_user)


@router.get("", response_model=list[UserResponse])
def list_users(
    current_user: User = Depends(require_roles(UserRole.OWNER, UserRole.ADMIN)),
    db: Session = Depends(get_db),
) -> list[UserResponse]:
    users = list_empresa_users(db, current_user.empresa_id)
    return [UserResponse.from_model(user) for user in users]


@router.post("/invites", response_model=UserInviteResponse)
def pre_register_user(
    payload: CreateUserInviteRequest,
    current_user: User = Depends(require_roles(UserRole.OWNER, UserRole.ADMIN)),
    db: Session = Depends(get_db),
) -> UserInviteResponse:
    role = UserRole[payload.role]

    if current_user.role == UserRole.ADMIN and role == UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin nao pode convidar outro admin",
        )

    subscription = require_empresa_subscription(db, current_user.empresa_id)
    plan_limit = get_plan_limit(subscription.plan_id)

    if role == UserRole.ADMIN:
        active_admins = count_active_users_by_role(db, current_user.empresa_id, UserRole.ADMIN)
        if active_admins >= plan_limit.max_admins:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Limite de admins do plano atingido",
            )

    if role == UserRole.MEMBER:
        active_members = count_active_users_by_role(db, current_user.empresa_id, UserRole.MEMBER)
        if active_members >= plan_limit.max_members:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Limite de membros do plano atingido",
            )

    existing = find_user_by_email(db, payload.email.strip().lower())
    if existing and existing.empresa_id == current_user.empresa_id:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ja existe usuario com este email na empresa",
        )

    invite, token = create_user_invite(
        db=db,
        empresa_id=current_user.empresa_id,
        invited_by_user_id=current_user.id,
        email=payload.email,
        role=role,
        expires_in_days=payload.expires_in_days,
    )

    return UserInviteResponse(
        id=invite.id,
        empresa_id=invite.empresa_id,
        email=invite.email,
        role=invite.role.value,
        status=invite.status.value,
        expires_at=invite.expires_at.isoformat(),
        invitation_token=token,
    )


@router.post("/invites/accept", response_model=UserResponse)
def accept_invite(payload: AcceptUserInviteRequest, db: Session = Depends(get_db)) -> UserResponse:
    invite = find_user_invite_by_token(db, payload.invite_token)
    if not invite:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Convite nao encontrado")

    assert_user_invite_available(invite)

    existing = find_user_by_email(db, invite.email.strip().lower())
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email ja utilizado",
        )

    user = create_user(
        db=db,
        empresa_id=invite.empresa_id,
        name=payload.name,
        email=invite.email,
        password_hash=hash_password(payload.password),
        role=invite.role,
        status=UserStatus.ACTIVE,
    )

    invite.status = UserInviteStatus.ACCEPTED
    invite.accepted_user_id = user.id
    db.add(invite)
    db.commit()

    return UserResponse.from_model(user)


@router.patch("/{user_id}/status", response_model=UserResponse)
def change_user_status(
    user_id: str,
    payload: UpdateUserStatusRequest,
    current_user: User = Depends(require_roles(UserRole.OWNER, UserRole.ADMIN)),
    db: Session = Depends(get_db),
) -> UserResponse:
    target_user = find_user_by_id(db, user_id)
    if not target_user or target_user.empresa_id != current_user.empresa_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario nao encontrado")

    if target_user.id == current_user.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Nao pode alterar o proprio status")

    if target_user.role == UserRole.OWNER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Owner nao pode ser desligado")

    if current_user.role == UserRole.ADMIN and target_user.role == UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Somente owner pode desligar admin",
        )

    new_status = UserStatus[payload.status]
    updated = update_user_status(db, target_user, new_status)
    return UserResponse.from_model(updated)
