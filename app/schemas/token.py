from pydantic import BaseModel, UUID4, Field
from typing import Optional


class TokenPayloadSchema(BaseModel):
    identity: UUID4
    exp: int
    type: str


class TokenCreationSchema(BaseModel):
    user_id: UUID4
    refresh_token: str
    access_token: str
    is_active: bool
    user_agent: Optional[str] = Field(default="")
    ip_address: Optional[str] = Field(default="")
