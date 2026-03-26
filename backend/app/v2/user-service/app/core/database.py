from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
import os
from .config import settings

# Base must be defined here and used by all models
Base = declarative_base()

# Handle postgresql:// vs postgresql+asyncpg://
database_url = os.getenv("DATABASE_URL", settings.DATABASE_URL)
if database_url.startswith("postgresql://"):
    database_url = database_url.replace("postgresql://", "postgresql+asyncpg://", 1)

# Use service-specific SQLite for tests to ensure isolation
if "sqlite" in database_url and ":memory:" in database_url:
    database_url = "sqlite+aiosqlite:///./test_user_service.db"

engine = create_async_engine(
    database_url,
    echo=False,
    future=True
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
