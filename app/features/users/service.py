from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.features.users.models import User


def find_user_by_email(db: Session, normalized_email: str) -> User | None:
    stmt = (
        select(User)
        .options(selectinload(User.empresa))
        .where(func.lower(User.email) == normalized_email)
    )
    return db.scalars(stmt).first()


def set_last_login_now(db: Session, user: User) -> None:
    user.last_login_at = datetime.now(timezone.utc)
    db.add(user)
    db.commit()
