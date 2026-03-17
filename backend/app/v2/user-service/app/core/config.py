from pydantic_settings import BaseSettings

from typing import Optional

class Settings(BaseSettings):
    DATABASE_URL: Optional[str] = "sqlite+aiosqlite:///:memory:"
    SECRET_KEY: str = "changeme"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    class Config:
        env_file = ".env"

settings = Settings()
