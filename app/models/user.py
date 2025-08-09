from sqlmodel import Field, SQLModel
from sqlalchemy import Column, DateTime, func
from datetime import datetime
from pydantic import EmailStr, field_validator
from passlib.context import CryptContext
import uuid, re

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class User(SQLModel, table=True):
    __tablename__ = "user"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, unique=True)
    first_name: str = Field(max_length=25, index=True)
    last_name: str = Field(max_length=25, index=True)
    username: str = Field(max_length=55, index=True, unique=True)
    email: EmailStr = Field(index=True, unique=True)
    password_hash: str
    is_active: bool = Field(default=False)
    is_email_verified: bool = Field(default=False)

    last_profile_updated_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True), server_default=func.now(), nullable=False
        )
    )

    last_password_updated_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True), server_default=func.now(), nullable=False
        )
    )

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

    # normalize BEFORE validation: remove all whitespace and lowercase
    @field_validator("first_name", "last_name", "username", "email", mode="before")
    @classmethod
    def _normalize_identifiers(cls, v):
        if v is None:
            return v
        v = re.sub(r"\s+", "", str(v))
        return v.lower()

    def set_password(self, raw_password: str):
        self.password_hash = pwd_context.hash(raw_password)

    def verify_password(self, raw_password: str) -> bool:
        return pwd_context.verify(raw_password, self.password_hash)

    def get_full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"
