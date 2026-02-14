from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.features.empresas.models import Empresa, EmpresaAddress, EmpresaPhone


def get_empresa_with_contacts(db: Session, empresa_id: str) -> Empresa | None:
    stmt = (
        select(Empresa)
        .options(selectinload(Empresa.addresses), selectinload(Empresa.phones))
        .where(Empresa.id == empresa_id)
    )
    return db.scalars(stmt).first()


def list_empresas(db: Session) -> list[Empresa]:
    stmt = (
        select(Empresa)
        .options(selectinload(Empresa.addresses), selectinload(Empresa.phones))
        .order_by(Empresa.created_at.desc())
    )
    return list(db.scalars(stmt).all())


def require_empresa_with_contacts(db: Session, empresa_id: str) -> Empresa:
    empresa = get_empresa_with_contacts(db, empresa_id)
    if not empresa:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Empresa nao encontrada")
    return empresa


def update_empresa(db: Session, empresa: Empresa, payload) -> Empresa:
    if payload.razao_social is not None:
        empresa.razao_social = payload.razao_social
    if payload.nome_fantasia is not None:
        empresa.nome_fantasia = payload.nome_fantasia
    if payload.cnpj is not None:
        empresa.cnpj = payload.cnpj

    if payload.address:
        primary_address = next((item for item in empresa.addresses if item.is_primary), None)
        if primary_address is None:
            primary_address = EmpresaAddress(empresa_id=empresa.id, is_primary=True)
        primary_address.street = payload.address.street
        primary_address.number = payload.address.number
        primary_address.complement = payload.address.complement
        primary_address.district = payload.address.district
        primary_address.city = payload.address.city
        primary_address.state = payload.address.state
        primary_address.zip_code = payload.address.zip_code
        db.add(primary_address)

    if payload.phone:
        primary_phone = next((item for item in empresa.phones if item.is_primary), None)
        if primary_phone is None:
            primary_phone = EmpresaPhone(empresa_id=empresa.id, is_primary=True)
        primary_phone.label = payload.phone.label
        primary_phone.phone_number = payload.phone.phone_number
        primary_phone.is_whatsapp = payload.phone.is_whatsapp
        db.add(primary_phone)

    db.add(empresa)
    db.commit()
    refreshed = get_empresa_with_contacts(db, empresa.id)
    if not refreshed:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Empresa nao encontrada")
    return refreshed
