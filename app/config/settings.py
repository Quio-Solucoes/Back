import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
EXCEL_FILE = BASE_DIR / "orcamento_final.xlsx"
ORCAMENTOS_DIR = BASE_DIR / "orcamentos"
SQLITE_DB_PATH = Path(os.getenv("SQLITE_DB_PATH", str(BASE_DIR / "quio.sqlite3")))
APP_ENV = os.getenv("APP_ENV", os.getenv("ENV", "development")).lower()

SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-me")
ACCESS_TOKEN_EXPIRE_SECONDS = int(os.getenv("ACCESS_TOKEN_EXPIRE_SECONDS", "3600"))

PASSWORD_HASHER = os.getenv("PASSWORD_HASHER", "pbkdf2_sha256").lower()
PBKDF2_ITERATIONS = int(os.getenv("PBKDF2_ITERATIONS", "260000"))

# Argon2id params (used only if PASSWORD_HASHER=argon2id and argon2-cffi installed)
ARGON2_TIME_COST = int(os.getenv("ARGON2_TIME_COST", "3"))
ARGON2_MEMORY_COST = int(os.getenv("ARGON2_MEMORY_COST", "65536"))  # KiB (64 MiB)
ARGON2_PARALLELISM = int(os.getenv("ARGON2_PARALLELISM", "1"))
ARGON2_HASH_LEN = int(os.getenv("ARGON2_HASH_LEN", "32"))
ARGON2_SALT_LEN = int(os.getenv("ARGON2_SALT_LEN", "16"))

CORS_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://www.quio.com.br",
    "https://quio.com.br",
]

# Em producao, default fechado (usa apenas CORS_ORIGINS).
# Em desenvolvimento, default aberto para facilitar testes locais.
_default_cors_allow_all = "false" if APP_ENV in {"prod", "production"} else "true"
CORS_ALLOW_ALL = os.getenv("CORS_ALLOW_ALL", _default_cors_allow_all).lower() == "true"


