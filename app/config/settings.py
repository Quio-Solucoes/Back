import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
EXCEL_FILE = BASE_DIR / "orcamento_final.xlsx"
ORCAMENTOS_DIR = BASE_DIR / "orcamentos"
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./app.db")
INTERNAL_API_KEY = os.getenv("INTERNAL_API_KEY", "change-internal-key")

CORS_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://www.quio.com.br",
    "https://quio.com.br",
]

# Development default: libera qualquer origem.
# Defina CORS_ALLOW_ALL=false para voltar ao modo restrito por lista.
CORS_ALLOW_ALL = os.getenv("CORS_ALLOW_ALL", "true").lower() == "true"


