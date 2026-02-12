from pathlib import Path

import uvicorn

from app.config.settings import ORCAMENTOS_DIR


if __name__ == "__main__":
    Path(ORCAMENTOS_DIR).mkdir(parents=True, exist_ok=True)
    uvicorn.run("app.main:app", host="127.0.0.1", port=5001, reload=True)
