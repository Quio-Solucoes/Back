from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
EXCEL_FILE = BASE_DIR / "orcamento_final.xlsx"
ORCAMENTOS_DIR = BASE_DIR / "orcamentos"

CORS_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]
