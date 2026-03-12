from fastapi import HTTPException, status
from app.features.common.address.schema import Address, UserAddressLink
from app.features.common.address import repository
from sqlalchemy.orm import Session



def upsert_empresa_address(db: Session, *, empresa_id: str, address_payload) -> Address:
    return repository.upsert_empresa_address(db, empresa_id=empresa_id, payload=address_payload)


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


def ensure_user_has_address(db: Session, *, user_id: str) -> list[UserAddressLink]:
    links = repository.list_user_address_links(db, user_id)
    if not links:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario sem enderecos")
    return links
