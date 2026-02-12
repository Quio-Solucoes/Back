from typing import Any

from pydantic import BaseModel


class ChatRequest(BaseModel):
    message: str = ""
    session_id: str = "default"


class ChatResponse(BaseModel):
    response: str
    options: list[dict[str, Any]] | None = None
    pdf_ready: bool | None = None
    pdf_filename: str | None = None
    download_url: str | None = None
