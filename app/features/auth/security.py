import base64
import hashlib
import hmac
import json
import secrets
import time
from dataclasses import dataclass

from app.config.settings import (
    ARGON2_HASH_LEN,
    ARGON2_MEMORY_COST,
    ARGON2_PARALLELISM,
    ARGON2_SALT_LEN,
    ARGON2_TIME_COST,
    PASSWORD_HASHER,
    PBKDF2_ITERATIONS,
)

try:
    from argon2 import PasswordHasher as _Argon2PasswordHasher  # type: ignore
except Exception:  # pragma: no cover
    _Argon2PasswordHasher = None


def _b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _b64url_decode(data: str) -> bytes:
    padding = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode((data + padding).encode("ascii"))


def _hash_password_pbkdf2_sha256(password: str, *, iterations: int) -> str:
    if not isinstance(password, str) or not password:
        raise ValueError("Senha invalida")

    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
    return f"pbkdf2_sha256${iterations}${_b64url_encode(salt)}${_b64url_encode(digest)}"


def _verify_password_pbkdf2_sha256(password: str, password_hash: str) -> bool:
    try:
        algo, iter_str, salt_b64, digest_b64 = password_hash.split("$", 3)
        if algo != "pbkdf2_sha256":
            return False
        iterations = int(iter_str)
        salt = _b64url_decode(salt_b64)
        expected = _b64url_decode(digest_b64)
    except Exception:
        return False

    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
    return hmac.compare_digest(digest, expected)


def _hash_password_argon2id(password: str) -> str:
    if _Argon2PasswordHasher is None:
        raise RuntimeError("argon2-cffi nao instalado (adicione 'argon2-cffi' no requirements)")

    hasher = _Argon2PasswordHasher(
        time_cost=ARGON2_TIME_COST,
        memory_cost=ARGON2_MEMORY_COST,
        parallelism=ARGON2_PARALLELISM,
        hash_len=ARGON2_HASH_LEN,
        salt_len=ARGON2_SALT_LEN,
    )
    # encoded includes the algorithm, salt and hash ($argon2id$...)
    encoded = hasher.hash(password)
    return f"argon2id${encoded}"


def _verify_password_argon2id(password: str, password_hash: str) -> bool:
    if not password_hash.startswith("argon2id$"):
        return False

    if _Argon2PasswordHasher is None:
        return False

    encoded = password_hash.split("$", 1)[1]
    hasher = _Argon2PasswordHasher(
        time_cost=ARGON2_TIME_COST,
        memory_cost=ARGON2_MEMORY_COST,
        parallelism=ARGON2_PARALLELISM,
        hash_len=ARGON2_HASH_LEN,
        salt_len=ARGON2_SALT_LEN,
    )

    try:
        return bool(hasher.verify(encoded, password))
    except Exception:
        return False


def needs_rehash(password_hash: str) -> bool:
    if password_hash.startswith("pbkdf2_sha256$"):
        try:
            _, iter_str, _, _ = password_hash.split("$", 3)
            return int(iter_str) != int(PBKDF2_ITERATIONS)
        except Exception:
            return True

    if password_hash.startswith("argon2id$"):
        # If argon2 isn't installed, we can't evaluate; avoid infinite rehash attempts.
        if _Argon2PasswordHasher is None:
            return False
        encoded = password_hash.split("$", 1)[1]
        hasher = _Argon2PasswordHasher(
            time_cost=ARGON2_TIME_COST,
            memory_cost=ARGON2_MEMORY_COST,
            parallelism=ARGON2_PARALLELISM,
            hash_len=ARGON2_HASH_LEN,
            salt_len=ARGON2_SALT_LEN,
        )
        try:
            return bool(hasher.check_needs_rehash(encoded))
        except Exception:
            return True

    return True


def hash_password(password: str) -> str:
    algo = str(PASSWORD_HASHER or "").strip().lower()
    if algo == "argon2id":
        return _hash_password_argon2id(password)
    if algo == "pbkdf2_sha256":
        return _hash_password_pbkdf2_sha256(password, iterations=PBKDF2_ITERATIONS)

    raise ValueError(f"PASSWORD_HASHER invalido: {PASSWORD_HASHER}")


def verify_password(password: str, password_hash: str) -> bool:
    if password_hash.startswith("argon2id$"):
        return _verify_password_argon2id(password, password_hash)

    if password_hash.startswith("pbkdf2_sha256$"):
        return _verify_password_pbkdf2_sha256(password, password_hash)

    return False


@dataclass(frozen=True)
class TokenPayload:
    sub: str
    exp: int


def create_access_token(subject: str, *, secret_key: str, expires_in_seconds: int) -> str:
    header = {"alg": "HS256", "typ": "JWT"}
    now = int(time.time())
    payload = {"sub": subject, "exp": now + int(expires_in_seconds)}

    header_b64 = _b64url_encode(json.dumps(header, separators=(",", ":"), ensure_ascii=False).encode("utf-8"))
    payload_b64 = _b64url_encode(json.dumps(payload, separators=(",", ":"), ensure_ascii=False).encode("utf-8"))
    signing_input = f"{header_b64}.{payload_b64}".encode("ascii")
    signature = hmac.new(secret_key.encode("utf-8"), signing_input, hashlib.sha256).digest()
    return f"{header_b64}.{payload_b64}.{_b64url_encode(signature)}"


def decode_access_token(token: str, *, secret_key: str) -> TokenPayload:
    try:
        header_b64, payload_b64, signature_b64 = token.split(".", 2)
    except ValueError as exc:
        raise ValueError("Token invalido") from exc

    signing_input = f"{header_b64}.{payload_b64}".encode("ascii")
    expected_sig = hmac.new(secret_key.encode("utf-8"), signing_input, hashlib.sha256).digest()
    actual_sig = _b64url_decode(signature_b64)
    if not hmac.compare_digest(expected_sig, actual_sig):
        raise ValueError("Token invalido")

    try:
        payload = json.loads(_b64url_decode(payload_b64).decode("utf-8"))
    except Exception as exc:
        raise ValueError("Token invalido") from exc

    exp = int(payload.get("exp", 0))
    sub = str(payload.get("sub", "")).strip()
    if not sub:
        raise ValueError("Token invalido")

    now = int(time.time())
    if exp <= now:
        raise ValueError("Token expirado")

    return TokenPayload(sub=sub, exp=exp)
