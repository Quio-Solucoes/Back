from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.features.contacts.service import set_empresa_contacts
from app.features.empresas import repository
from app.features.empresas.schema import Empresa


def get_empresa_with_contacts(db: Session, empresa_id: str) -> Empresa | None:
    return repository.get_empresa_with_contacts(db, empresa_id)


def list_empresas(db: Session) -> list[Empresa]:
    return repository.list_empresas_with_contacts(db)


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

    set_empresa_contacts(
        db,
        empresa_id=empresa.id,
        address_payload=payload.address,
        phone_payload=payload.phone,
    )

    db.add(empresa)
    db.commit()
    refreshed = get_empresa_with_contacts(db, empresa.id)
    if not refreshed:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Empresa nao encontrada")
    return refreshed
