from app.features.common.address.schema import Address
from app.features.common.phones.schema import Phone
from app.features.common.phones import repository
from app.features.common.address import repository

from sqlalchemy.orm import Session

def set_empresa_contacts(db: Session, *, empresa_id: str, address_payload=None, phone_payload=None) -> tuple[Address | None, Phone | None]:
    address = None
    phone = None

    if address_payload is not None:
        address = repository.upsert_empresa_address(db, empresa_id=empresa_id, payload=address_payload)

    if phone_payload is not None:
        phone = repository.upsert_empresa_primary_phone(db, empresa_id=empresa_id, payload=phone_payload)

    return address, phone
