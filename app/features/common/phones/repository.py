from app.features.common.phones.schema import Phone
from sqlalchemy import delete, select, update
from sqlalchemy.orm import Session, selectinload


def get_empresa_phones(db: Session, empresa_id: str) -> list[Phone]:
    stmt = (
        select(Phone)
        .where(Phone.empresa_id == empresa_id)
        .order_by(Phone.is_primary.desc(), Phone.created_at.asc())
    )
    return list(db.scalars(stmt).all())


def upsert_empresa_primary_phone(db: Session, *, empresa_id: str, payload) -> Phone:
    stmt = select(Phone).where(Phone.empresa_id == empresa_id).where(Phone.is_primary.is_(True))
    phone = db.scalars(stmt).first()
    if phone is None:
        phone = Phone(empresa_id=empresa_id, is_primary=True)

    phone.label = payload.label
    phone.phone_number = payload.phone_number
    phone.is_whatsapp = payload.is_whatsapp
    db.add(phone)
    return phone


def list_user_phones(db: Session, user_id: str) -> list[Phone]:
    stmt = (
        select(Phone)
        .where(Phone.user_id == user_id)
        .order_by(Phone.is_primary.desc(), Phone.created_at.asc())
    )
    return list(db.scalars(stmt).all())


def create_user_phone(db: Session, *, user_id: str, payload, is_primary: bool = False) -> Phone:
    if is_primary:
        db.execute(update(Phone).where(Phone.user_id == user_id).values(is_primary=False))

    phone = Phone(
        user_id=user_id,
        label=payload.label,
        phone_number=payload.phone_number,
        is_whatsapp=payload.is_whatsapp,
        is_primary=is_primary,
    )
    db.add(phone)
    return phone
