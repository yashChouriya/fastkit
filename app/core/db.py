from sqlmodel import Session, SQLModel, create_engine
from urllib.parse import quote_plus
from typing import Iterator
import os


def get_db_url():
    from dotenv import load_dotenv

    load_dotenv()

    config = {
        "pg_username": os.getenv("POSTGRES_USER", None),
        "pg_password": os.getenv("POSTGRES_PASSWORD", None),
        "pg_host": os.getenv("POSTGRES_HOST", None),
        "pg_port": os.getenv("POSTGRES_PORT", None),
        "pg_db_name": os.getenv("POSTGRES_DB", None),
    }

    for config_name, value in config.items():
        if not value:
            raise RuntimeError(f"DATABASE ENV VAR {config_name}, NOT INITIALIZED!")

    # percent-encode any special chars in username or pass
    user_enc = quote_plus(config["pg_username"])
    pass_enc = quote_plus(config["pg_password"])
    host = config["pg_host"]
    port = int(config["pg_port"])
    db = config["pg_db_name"]

    db_connection_url = f"postgresql://{user_enc}:{pass_enc}@{host}:{port}/{db}"

    return db_connection_url


DATABASE_URL = get_db_url()

engine = create_engine(
    DATABASE_URL,
    echo=os.getenv("SQL_ECHO", "0") == "1",
    pool_pre_ping=True,  # drops dead connections
    pool_recycle=1800,  # avoids stale connections (secs)
)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session() -> Iterator[Session]:
    with Session(engine) as session:
        yield session
