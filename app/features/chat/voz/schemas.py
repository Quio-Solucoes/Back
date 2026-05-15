from pydantic import BaseModel, Field


class ChatVoiceRequest(BaseModel):
    message: str = Field(default="", min_length=0, max_length=4000)
    session_id: str = Field(default="default", min_length=1, max_length=255)
