from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.features.empresas.schema import Empresa


def get_empresa_with_contacts(db: Session, empresa_id: str) -> Empresa | None:
    stmt = (
        select(Empresa)
        .options(selectinload(Empresa.address), selectinload(Empresa.phones))
        .where(Empresa.id == empresa_id)
    )
    return db.scalars(stmt).first()


def list_empresas_with_contacts(db: Session) -> list[Empresa]:
    stmt = (
        select(Empresa)
        .options(selectinload(Empresa.address), selectinload(Empresa.phones))
        .order_by(Empresa.created_at.desc())
    )
    return list(db.scalars(stmt).all())


def get_empresa_by_id(db: Session, empresa_id: str) -> Empresa | None:
    return db.get(Empresa, empresa_id)
