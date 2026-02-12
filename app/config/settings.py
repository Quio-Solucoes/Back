from pathlib import Path
from fastapi.middleware.cors import CORSMiddleware

BASE_DIR = Path(__file__).resolve().parents[2]
EXCEL_FILE = BASE_DIR / "orcamento_final.xlsx"
ORCAMENTOS_DIR = BASE_DIR / "orcamentos"

CORS_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    # Se você quer liberar "o resto", use ["*"]
    allow_origins=["*"], 
    # IMPORTANTE: Se usar ["*"], allow_credentials deve ser False
    allow_credentials=False, 
    allow_methods=["*"],
    allow_headers=["*"],
)
