from pathlib import Path


class Settings:
    root_path: str = "/api/v1"
    redirect_slashes: bool = True
    app_title: str = "FastKit"
    app_description: str = (
        "A modular FastAPI starter kit with PostgreSQL, SQLAlchemy, JWT auth, and WebSocket support."
    )

    class Config:
        env_file: str = str(Path(__file__).parent.parent / ".env")
        env_file_encoding: str = "utf-8"


settings = Settings()
