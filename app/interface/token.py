from pydantic import BaseModel, EmailStr, UUID4


class TokenPayload(BaseModel):
    identity: UUID4
    exp: int
    type: str
