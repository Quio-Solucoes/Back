import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
EXCEL_FILE = BASE_DIR / "orcamento_final.xlsx"
ORCAMENTOS_DIR = BASE_DIR / "orcamentos"
APP_ENV = os.getenv("APP_ENV", os.getenv("ENV", "development")).lower()

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


