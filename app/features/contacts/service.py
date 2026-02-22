from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.features.contacts import repository
from app.features.contacts.schema import Address, Phone, UserAddressLink


def set_empresa_contacts(db: Session, *, empresa_id: str, address_payload=None, phone_payload=None) -> tuple[Address | None, Phone | None]:
    address = None
    phone = None

    if address_payload is not None:
        address = repository.upsert_empresa_address(db, empresa_id=empresa_id, payload=address_payload)

    if phone_payload is not None:
        phone = repository.upsert_empresa_primary_phone(db, empresa_id=empresa_id, payload=phone_payload)

    return address, phone


def list_user_addresses(db: Session, *, user_id: str) -> list[UserAddressLink]:
    return repository.list_user_address_links(db, user_id)


def add_new_address_to_user(
    db: Session,
    *,
    user_id: str,
    address_payload,
    is_primary: bool = False,
    label: str | None = None,
) -> UserAddressLink:
    address = repository.create_address(db, address_payload)
    db.flush()
    link = repository.attach_address_to_user(
        db,
        user_id=user_id,
        address_id=address.id,
        is_primary=is_primary,
        label=label,
    )
    return link


def link_existing_address_to_user(
    db: Session,
    *,
    user_id: str,
    address: Address,
    is_primary: bool = False,
    label: str | None = None,
) -> UserAddressLink:
    return repository.attach_address_to_user(
        db,
        user_id=user_id,
        address_id=address.id,
        is_primary=is_primary,
        label=label,
    )


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


def ensure_user_has_address(db: Session, *, user_id: str) -> list[UserAddressLink]:
    links = repository.list_user_address_links(db, user_id)
    if not links:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario sem enderecos")
    return links
