from pydantic_settings import BaseSettings

from typing import Optional

class Settings(BaseSettings):
    # default to in‑memory SQLite so tests can import without env vars
    DATABASE_URL: Optional[str] = "sqlite+aiosqlite:///:memory:"

    class Config:
        env_file = ".env"

settings = Settings()