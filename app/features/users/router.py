from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.db import get_db
from app.features.auth.dependencies import get_current_user, require_roles
from app.features.contacts.dtos import (
    UserAddressCreateRequest,
    UserAddressLinkResponse,
    UserPhoneCreateRequest,
    UserPhoneResponse,
)
from app.features.contacts.address_service import add_new_address_to_user, list_user_addresses
from app.features.contacts.phone_service import add_user_phone, list_user_phones
from app.features.identity.repository import get_by_login_identifier
from app.features.identity.service import create_auth_account
from app.features.invites.enums import UserInviteStatus
from app.features.invites.service import (
    assert_user_invite_available,
    create_user_invite,
    find_user_invite_by_token,
)
from app.features.memberships.enums import MembershipRole, MembershipStatus
from app.features.memberships.service import create_membership
from app.features.subscriptions.plans import get_plan_limit
from app.features.subscriptions.service import require_empresa_subscription
from app.features.users.dtos import (
    AcceptUserInviteRequest,
    CreateUserInviteRequest,
    UpdateUserStatusRequest,
    UserInviteResponse,
    UserResponse,
)
from app.features.users.enums import UserStatus
from app.features.users.service import (
    count_active_users_by_role,
    count_active_users_by_roles,
    create_user,
    find_user_by_email,
    find_user_by_id,
    list_empresa_users,
    update_user_status,
)
from app.features.users.schema import User


router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserResponse)
def me(current_user: User = Depends(get_current_user)) -> UserResponse:
    return UserResponse.from_model(current_user)


@router.get("/me/addresses", response_model=list[UserAddressLinkResponse])
def me_addresses(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[UserAddressLinkResponse]:
    links = list_user_addresses(db, user_id=current_user.id)
    return [UserAddressLinkResponse.from_model(link) for link in links]


@router.post("/me/addresses", response_model=UserAddressLinkResponse, status_code=status.HTTP_201_CREATED)
def add_me_address(
    payload: UserAddressCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> UserAddressLinkResponse:
    link = add_new_address_to_user(
        db,
        user_id=current_user.id,
        address_payload=payload.address,
        is_primary=payload.is_primary,
        label=payload.label,
    )
    db.commit()
    links = list_user_addresses(db, user_id=current_user.id)
    created = next((item for item in links if item.id == link.id), None)
    if created is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Falha ao carregar endereco criado")
    return UserAddressLinkResponse.from_model(created)


@router.post("/me/phones", response_model=UserPhoneResponse, status_code=status.HTTP_201_CREATED)
def add_me_phone(
    payload: UserPhoneCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> UserPhoneResponse:
    phone = add_user_phone(
        db,
        user_id=current_user.id,
        phone_payload=payload.phone,
        is_primary=payload.is_primary,
    )
    db.commit()
    db.refresh(phone)
    return UserPhoneResponse.from_model(phone)


@router.get("/me/phones", response_model=list[UserPhoneResponse])
def me_phones(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[UserPhoneResponse]:
    phones = list_user_phones(db, user_id=current_user.id)
    return [UserPhoneResponse.from_model(phone) for phone in phones]


@router.get("", response_model=list[UserResponse])
def list_users(
    current_user: User = Depends(require_roles(MembershipRole.OWNER, MembershipRole.ADMIN)),
    db: Session = Depends(get_db),
) -> list[UserResponse]:
    users = list_empresa_users(db, current_user.empresa_id)
    return [UserResponse.from_model(user) for user in users]


@router.post("/invites", response_model=UserInviteResponse)
def pre_register_user(
    payload: CreateUserInviteRequest,
    current_user: User = Depends(require_roles(MembershipRole.OWNER, MembershipRole.ADMIN)),
    db: Session = Depends(get_db),
) -> UserInviteResponse:
    role = MembershipRole[payload.role]

    if current_user.role == MembershipRole.ADMIN and role == MembershipRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin nao pode convidar outro admin",
        )

    subscription = require_empresa_subscription(db, current_user.empresa_id)
    plan_limit = get_plan_limit(subscription.plan_id)

    if role in {MembershipRole.ADMIN, MembershipRole.GESTOR_COMERCIAL}:
        active_admins = count_active_users_by_roles(
            db,
            current_user.empresa_id,
            [MembershipRole.ADMIN, MembershipRole.GESTOR_COMERCIAL],
        )
        if active_admins >= plan_limit.max_admins:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Limite de admins do plano atingido",
            )

    if role in {MembershipRole.COLABORADOR, MembershipRole.CONSULTOR}:
        active_members = count_active_users_by_roles(
            db,
            current_user.empresa_id,
            [MembershipRole.COLABORADOR, MembershipRole.CONSULTOR],
        )
        if active_members >= plan_limit.max_members:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Limite de membros do plano atingido",
            )

    normalized_email = payload.email.strip().lower()
    existing_account = get_by_login_identifier(db, normalized_email)
    if existing_account and any(m.empresa_id == current_user.empresa_id for m in existing_account.user.memberships):
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

    normalized_email = invite.email.strip().lower()
    existing_user = find_user_by_email(db, normalized_email)
    existing_account = get_by_login_identifier(db, normalized_email)
    if existing_user or existing_account:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Identificador de login ja utilizado",
        )

    user = create_user(
        db=db,
        name=payload.name,
        primary_email=invite.email,
        status=UserStatus.ACTIVE,
    )

    create_auth_account(
        db=db,
        user_id=user.id,
        login_identifier=invite.email,
        password=payload.password,
    )

    create_membership(
        db=db,
        user_id=user.id,
        empresa_id=invite.empresa_id,
        role=invite.role,
        status=MembershipStatus.ACTIVE,
        is_default=True,
        invited_by=invite.invited_by_user_id,
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
    current_user: User = Depends(require_roles(MembershipRole.OWNER, MembershipRole.ADMIN)),
    db: Session = Depends(get_db),
) -> UserResponse:
    target_user = find_user_by_id(db, user_id)
    if not target_user or target_user.empresa_id != current_user.empresa_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario nao encontrado")

    if target_user.id == current_user.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Nao pode alterar o proprio status")

    if target_user.role == MembershipRole.OWNER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Owner nao pode ser desligado")

    if current_user.role == MembershipRole.ADMIN and target_user.role == MembershipRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Somente owner pode desligar admin",
        )

    new_status = UserStatus[payload.status]
    updated = update_user_status(db, target_user, new_status)
    return UserResponse.from_model(updated)
