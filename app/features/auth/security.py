from datetime import datetime, timedelta, timezone
from typing import Any

from jose import jwt

from app.features.auth.config import ACCESS_TOKEN_EXPIRE_MINUTES, JWT_ALG, JWT_SECRET


def create_access_token(data: dict[str, Any], expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALG)
