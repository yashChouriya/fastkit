from sqlmodel import Field, Session, SQLModel, create_engine
from sqlalchemy import Column, DateTime, func
from datetime import datetime
from pydantic import EmailStr, IPvAnyAddress
from passlib.context import CryptContext
from urllib.parse import quote_plus
from typing import Optional
import uuid
import os


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, unique=True)
    first_name: str = Field(max_length=25, index=True)
    last_name: str = Field(max_length=25, index=True)
    username: str = Field(max_length=55, index=True, unique=True)
    email: EmailStr = Field(index=True, unique=True)
    password_hash: str
    is_active: bool = Field(default=False)

    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(
            DateTime(timezone=True),
            server_default=func.now(),
            nullable=False,
        ),
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(
            DateTime(timezone=True),
            server_default=func.now(),
            onupdate=func.now(),
            nullable=False,
        ),
    )

    def set_password(self, raw_password: str):
        self.password_hash = pwd_context.hash(raw_password)

    def verify_password(self, raw_password: str) -> bool:
        return pwd_context.verify(raw_password, self.password_hash)

    def get_full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"


class Token(SQLModel, table=True):
    __tablename__ = "tokens"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, unique=True)
    user_id: uuid.UUID = Field(foreign_key="user.id")
    refresh_token: str = Field()
    access_token: str = Field()
    is_active: bool = Field(default=False)
    user_agent: Optional[str] = Field(default="")
    ip_address: Optional[IPvAnyAddress] = Field(default="")

    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(
            DateTime(timezone=True),
            server_default=func.now(),
            nullable=False,
        ),
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(
            DateTime(timezone=True),
            server_default=func.now(),
            onupdate=func.now(),
            nullable=False,
        ),
    )


DB_USER = os.getenv("POSTGRES_USER")
DB_PASS = os.getenv("POSTGRES_PASSWORD")
DB_HOST = os.getenv("POSTGRES_HOST")
DB_PORT = os.getenv("POSTGRES_PORT")
DB_NAME = os.getenv("POSTGRES_DB")

# percent-encode any special chars in user or pass
user_enc = quote_plus(DB_USER)
pass_enc = quote_plus(DB_PASS)

DATABASE_URL = f"postgresql://{user_enc}:{pass_enc}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(DATABASE_URL, echo=True)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session
