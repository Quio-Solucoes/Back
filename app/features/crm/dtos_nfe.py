from pydantic import BaseModel


class EnableNfeRequest(BaseModel):
    enable: bool = True


class EnableNfeResponse(BaseModel):
    lead_id: str
    nfe_enabled: bool
