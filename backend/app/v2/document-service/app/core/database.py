from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from .config import settings
import os
from sqlalchemy.pool import StaticPool

# Handle postgresql:// vs postgresql+asyncpg://
database_url = os.getenv("DATABASE_URL", settings.DATABASE_URL)
if database_url.startswith("postgresql://"):
    database_url = database_url.replace("postgresql://", "postgresql+asyncpg://", 1)

engine_kwargs = {}
if database_url.startswith("sqlite"):
    engine_kwargs["poolclass"] = StaticPool

engine = create_async_engine(
    database_url,
    echo=settings.DEBUG,
    future=True,
    **engine_kwargs
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

Base = declarative_base()

async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
