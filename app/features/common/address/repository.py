from sqlalchemy import delete, select, update
from sqlalchemy.orm import Session, selectinload

from app.features.common.address.schema import Address, UserAddressLink 


def get_empresa_address(db: Session, empresa_id: str) -> Address | None:
    stmt = select(Address).where(Address.empresa_id == empresa_id)
    return db.scalars(stmt).first()


def upsert_empresa_address(db: Session, *, empresa_id: str, payload) -> Address:
    address = get_empresa_address(db, empresa_id)
    if address is None:
        address = Address(empresa_id=empresa_id)

    address.street = payload.street
    address.number = payload.number
    address.complement = payload.complement
    address.district = payload.district
    address.city = payload.city
    address.state = payload.state
    address.zip_code = payload.zip_code
    db.add(address)
    return address


def list_user_address_links(db: Session, user_id: str) -> list[UserAddressLink]:
    stmt = (
        select(UserAddressLink)
        .options(selectinload(UserAddressLink.address))
        .where(UserAddressLink.user_id == user_id)
        .order_by(UserAddressLink.is_primary.desc(), UserAddressLink.created_at.asc())
    )
    return list(db.scalars(stmt).all())


def create_address(db: Session, payload, *, empresa_id: str | None = None) -> Address:
    address = Address(
        empresa_id=empresa_id,
        street=payload.street,
        number=payload.number,
        complement=payload.complement,
        district=payload.district,
        city=payload.city,
        state=payload.state,
        zip_code=payload.zip_code,
    )
    db.add(address)
    return address


def attach_address_to_user(
    db: Session,
    *,
    user_id: str,
    address_id: str,
    is_primary: bool = False,
    label: str | None = None,
) -> UserAddressLink:
    if is_primary:
        db.execute(update(UserAddressLink).where(UserAddressLink.user_id == user_id).values(is_primary=False))

    link = UserAddressLink(user_id=user_id, address_id=address_id, is_primary=is_primary, label=label)
    db.add(link)
    return link


def remove_user_address_link(db: Session, *, user_id: str, address_id: str) -> int:
    stmt = delete(UserAddressLink).where(UserAddressLink.user_id == user_id).where(UserAddressLink.address_id == address_id)
    result = db.execute(stmt)
    return int(result.rowcount or 0)
