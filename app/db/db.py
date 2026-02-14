from collections.abc import Generator

from app.config.settings import DATABASE_URL
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker




class Base(DeclarativeBase):
    pass


connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, future=True, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    import app.features.empresas.models  # noqa: F401
    import app.features.invites.models  # noqa: F401
    import app.features.subscriptions.models  # noqa: F401
    import app.features.users.models  # noqa: F401

    Base.metadata.create_all(bind=engine)
