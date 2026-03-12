from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.features.auth.identity.service import (
    create_auth_account,
    find_auth_account_by_login_identifier,
)
from app.features.common.service import set_empresa_contacts
from app.features.empresas.enums import EmpresaStatus
from app.features.empresas.invites.enums import FranchiseInviteStatus
from app.features.empresas.invites.service import (
    assert_invite_available,
    find_franchise_invite_by_registered_empresa_id,
    find_franchise_invite_by_token,
)
from app.features.empresas.memberships.enums import MembershipRole, MembershipStatus
from app.features.empresas.memberships.service import create_membership
from app.features.empresas.schema import Empresa
from app.features.empresas.service import find_empresa_by_id
from app.features.empresas.subscriptions.enums import BillingCycle, SubscriptionStatus
from app.features.empresas.subscriptions.schema import Subscription
from app.features.empresas.subscriptions.service import get_empresa_subscription
from app.features.users.enums import UserStatus
from app.features.users.schema import User
from app.features.users.service import find_user_by_empresa_and_role


def create_pending_company_and_owner(db: Session, payload) -> tuple[Empresa, User, Subscription]:
    invite = find_franchise_invite_by_token(db, payload.invite_token)
    if not invite:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Convite de franquia nao encontrado")

    assert_invite_available(invite)

    if payload.owner_email.strip().lower() != invite.email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email do owner deve ser o mesmo do convite",
        )

    normalized_email = payload.owner_email.strip().lower()
    if find_auth_account_by_login_identifier(db, normalized_email):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email do owner ja cadastrado")

    empresa = Empresa(
        razao_social=payload.razao_social,
        nome_fantasia=payload.nome_fantasia,
        cnpj=payload.cnpj,
        status=EmpresaStatus.PENDING_APPROVAL,
    )
    db.add(empresa)
    db.flush()

    owner = User(
        name=payload.owner_name,
        status=UserStatus.PENDING,
        primary_email=payload.owner_email,
    )
    db.add(owner)
    db.flush()

    create_auth_account(
        db,
        user_id=owner.id,
        login_identifier=payload.owner_email,
        password=payload.owner_password,
    )

    create_membership(
        db,
        user_id=owner.id,
        empresa_id=empresa.id,
        role=MembershipRole.OWNER,
        status=MembershipStatus.ACTIVE,
        is_default=True,
    )

    billing_cycle = BillingCycle[payload.billing_cycle]
    subscription = Subscription(
        empresa_id=empresa.id,
        plan_id=payload.plan_id.upper(),
        status=SubscriptionStatus.PENDING_PAYMENT,
        billing_cycle=billing_cycle,
        current_price=0,
    )

    invite.status = FranchiseInviteStatus.REGISTERED
    invite.registered_empresa_id = empresa.id

    set_empresa_contacts(
        db,
        empresa_id=empresa.id,
        address_payload=payload.address,
        phone_payload=payload.phone,
    )

    db.add_all([owner, subscription, invite])
    db.commit()
    db.refresh(empresa)
    db.refresh(owner)
    db.refresh(subscription)
    return empresa, owner, subscription


def get_owner(db: Session, empresa_id: str) -> User | None:
    return find_user_by_empresa_and_role(db, empresa_id, MembershipRole.OWNER)


def get_latest_subscription(db: Session, empresa_id: str) -> Subscription | None:
    return get_empresa_subscription(db, empresa_id)


def ensure_empresa(db: Session, empresa_id: str) -> Empresa:
    empresa = find_empresa_by_id(db, empresa_id)
    if not empresa:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Empresa nao encontrada")
    return empresa


def approve_empresa(db: Session, empresa_id: str) -> tuple[Empresa, User | None, Subscription | None]:
    empresa = ensure_empresa(db, empresa_id)
    if empresa.status == EmpresaStatus.REJECTED:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Empresa rejeitada nao pode ser aprovada")

    empresa.status = EmpresaStatus.SUSPENDED
    owner = get_owner(db, empresa.id)
    subscription = get_latest_subscription(db, empresa.id)

    franchise_invite = find_franchise_invite_by_registered_empresa_id(db, empresa.id)
    if franchise_invite:
        franchise_invite.status = FranchiseInviteStatus.APPROVED
        db.add(franchise_invite)

    db.add(empresa)
    db.commit()
    db.refresh(empresa)
    return empresa, owner, subscription


def reject_empresa(db: Session, empresa_id: str) -> tuple[Empresa, User | None, Subscription | None]:
    empresa = ensure_empresa(db, empresa_id)
    empresa.status = EmpresaStatus.REJECTED

    owner = get_owner(db, empresa.id)
    if owner:
        owner.status = UserStatus.SUSPENDED
        db.add(owner)

    subscription = get_latest_subscription(db, empresa.id)
    if subscription:
        subscription.status = SubscriptionStatus.CANCELED
        db.add(subscription)

    franchise_invite = find_franchise_invite_by_registered_empresa_id(db, empresa.id)
    if franchise_invite:
        franchise_invite.status = FranchiseInviteStatus.REJECTED
        db.add(franchise_invite)

    db.add(empresa)
    db.commit()
    db.refresh(empresa)
    return empresa, owner, subscription


def activate_owner_after_payment(db: Session, empresa_id: str) -> tuple[Empresa, User, Subscription | None]:
    empresa = ensure_empresa(db, empresa_id)
    if empresa.status in {EmpresaStatus.REJECTED, EmpresaStatus.CANCELED}:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Empresa com status invalido para ativacao",
        )

    owner = get_owner(db, empresa.id)
    if not owner:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Owner da empresa nao encontrado")

    subscription = get_latest_subscription(db, empresa.id)

    empresa.status = EmpresaStatus.ACTIVE
    owner.status = UserStatus.ACTIVE

    if subscription:
        subscription.status = SubscriptionStatus.ACTIVE
        db.add(subscription)

    db.add_all([empresa, owner])
    db.commit()
    db.refresh(empresa)
    db.refresh(owner)
    if subscription:
        db.refresh(subscription)

    return empresa, owner, subscription
