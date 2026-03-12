from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import datetime, timezone

from argon2 import PasswordHasher, Type
from argon2.exceptions import VerifyMismatchError

from app.features.auth.identity.schema import AuthAccount


@dataclass(frozen=True)
class PasswordHashPolicy:
    version: int
    memory_cost: int
    time_cost: int
    parallelism: int
    pepper_version: int


def _load_default_policy() -> PasswordHashPolicy:
    current_pepper_version = int(os.getenv("PASSWORD_PEPPER_CURRENT_VERSION", "1"))
    return PasswordHashPolicy(
        version=int(os.getenv("PASSWORD_HASH_POLICY_VERSION", "1")),
        memory_cost=int(os.getenv("PASSWORD_MEMORY_COST", "65536")),
        time_cost=int(os.getenv("PASSWORD_TIME_COST", "3")),
        parallelism=int(os.getenv("PASSWORD_PARALLELISM", "4")),
        pepper_version=current_pepper_version,
    )


DEFAULT_POLICY = _load_default_policy()
POLICIES: dict[int, PasswordHashPolicy] = {DEFAULT_POLICY.version: DEFAULT_POLICY}


def get_policy(version: int | None = None) -> PasswordHashPolicy:
    if version is not None and version in POLICIES:
        return POLICIES[version]
    return DEFAULT_POLICY


def _get_pepper(version: int) -> str:
    env_var = f"PASSWORD_PEPPER_V{version}"
    value = os.getenv(env_var)
    if not value:
        raise RuntimeError(f"Pepper {env_var} not configured")
    return value


def _build_hasher(policy: PasswordHashPolicy) -> PasswordHasher:
    return PasswordHasher(
        time_cost=policy.time_cost,
        memory_cost=policy.memory_cost,
        parallelism=policy.parallelism,
        hash_len=32,
        type=Type.ID,
    )


def hash_password(password: str, policy: PasswordHashPolicy | None = None) -> tuple[str, int, int]:
    policy = policy or DEFAULT_POLICY
    pepper = _get_pepper(policy.pepper_version)
    hasher = _build_hasher(policy)
    hashed = hasher.hash(password + pepper)
    return hashed, policy.version, policy.pepper_version


def verify_password(account: AuthAccount, password: str) -> bool:
    policy = get_policy(account.hash_policy_version)
    hasher = _build_hasher(policy)
    pepper = _get_pepper(account.pepper_version)
    try:
        return hasher.verify(account.password_hash, password + pepper)
    except VerifyMismatchError:
        return False


def needs_rehash(account: AuthAccount) -> bool:
    current_policy = DEFAULT_POLICY
    if account.hash_policy_version != current_policy.version or account.pepper_version != current_policy.pepper_version:
        return True
    hasher = _build_hasher(current_policy)
    return hasher.check_needs_rehash(account.password_hash)


def rehash_password(account: AuthAccount, password: str) -> None:
    new_hash, policy_version, pepper_version = hash_password(password, DEFAULT_POLICY)
    account.password_hash = new_hash
    account.hash_policy_version = policy_version
    account.pepper_version = pepper_version
    account.last_rehash_at = datetime.now(timezone.utc)
