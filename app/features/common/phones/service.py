from app.features.common.phones.schema import Phone
from app.features.common.phones import repository
from sqlalchemy.orm import Session



def upsert_empresa_primary_phone(db: Session, *, empresa_id: str, phone_payload) -> Phone:
    return repository.upsert_empresa_primary_phone(db, empresa_id=empresa_id, payload=phone_payload)


def add_user_phone(
    db: Session,
    *,
    user_id: str,
    phone_payload,
    is_primary: bool = False,
) -> Phone:
    return repository.create_user_phone(db, user_id=user_id, payload=phone_payload, is_primary=is_primary)


def list_user_phones(db: Session, *, user_id: str) -> list[Phone]:
    return repository.list_user_phones(db, user_id)
