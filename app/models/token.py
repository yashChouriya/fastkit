from sqlmodel import Field, SQLModel
from sqlalchemy import Column, DateTime, func
from datetime import datetime
from typing import Optional
import uuid


class Token(SQLModel, table=True):
    __tablename__ = "token"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, unique=True)
    user_id: uuid.UUID = Field(foreign_key="user.id")
    refresh_token: str = Field()
    access_token: str = Field()
    is_active: bool = Field(default=False)
    user_agent: Optional[str] = Field(default="")
    ip_address: Optional[str] = Field(default="", max_length=45)

    created_at: datetime = Field(
        default_factory=datetime.now,
        sa_column=Column(
            DateTime(timezone=True),
            server_default=func.now(),
            nullable=False,
        ),
    )
    updated_at: datetime = Field(
        default_factory=datetime.now,
        sa_column=Column(
            DateTime(timezone=True),
            server_default=func.now(),
            onupdate=func.now(),
            nullable=False,
        ),
    )
