from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.features.auth.security import hash_password
from app.features.empresas.enums import EmpresaStatus
from app.features.empresas.models import Empresa, EmpresaAddress, EmpresaPhone
from app.features.invites.enums import FranchiseInviteStatus
from app.features.invites.models import FranchiseInvite
from app.features.invites.service import assert_invite_available, find_franchise_invite_by_token
from app.features.subscriptions.enums import BillingCycle, SubscriptionStatus
from app.features.subscriptions.models import Subscription
from app.features.users.enums import UserRole, UserStatus
from app.features.users.models import User


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

    email_in_use_stmt = select(User).where(func.lower(User.email) == payload.owner_email.strip().lower())
    if db.scalars(email_in_use_stmt).first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email do owner ja cadastrado")

    empresa = Empresa(
        razao_social=payload.razao_social,
        nome_fantasia=payload.nome_fantasia,
        cnpj=payload.cnpj,
        status=EmpresaStatus.PENDING_APPROVAL,
    )
    db.add(empresa)
    db.flush()

    address = EmpresaAddress(
        empresa_id=empresa.id,
        street=payload.address.street,
        number=payload.address.number,
        complement=payload.address.complement,
        district=payload.address.district,
        city=payload.address.city,
        state=payload.address.state,
        zip_code=payload.address.zip_code,
        is_primary=True,
    )
    phone = EmpresaPhone(
        empresa_id=empresa.id,
        label=payload.phone.label,
        phone_number=payload.phone.phone_number,
        is_whatsapp=payload.phone.is_whatsapp,
        is_primary=True,
    )
    owner = User(
        empresa_id=empresa.id,
        name=payload.owner_name,
        email=payload.owner_email,
        password_hash=hash_password(payload.owner_password),
        role=UserRole.OWNER,
        status=UserStatus.PENDING,
        email_verified=True,
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

    db.add_all([address, phone, owner, subscription, invite])
    db.commit()
    db.refresh(empresa)
    db.refresh(owner)
    db.refresh(subscription)
    return empresa, owner, subscription


def get_owner(db: Session, empresa_id: str) -> User | None:
    stmt = (
        select(User)
        .where(User.empresa_id == empresa_id)
        .where(User.role == UserRole.OWNER)
    )
    return db.scalars(stmt).first()


def get_latest_subscription(db: Session, empresa_id: str) -> Subscription | None:
    stmt = (
        select(Subscription)
        .where(Subscription.empresa_id == empresa_id)
        .order_by(Subscription.started_at.desc())
    )
    return db.scalars(stmt).first()


def ensure_empresa(db: Session, empresa_id: str) -> Empresa:
    empresa = db.get(Empresa, empresa_id)
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

    invite_stmt = select(FranchiseInvite).where(FranchiseInvite.registered_empresa_id == empresa.id)
    franchise_invite = db.scalars(invite_stmt).first()
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

    invite_stmt = select(FranchiseInvite).where(FranchiseInvite.registered_empresa_id == empresa.id)
    franchise_invite = db.scalars(invite_stmt).first()
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
