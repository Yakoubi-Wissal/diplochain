"""
database.py — DiploChain
Engine async PostgreSQL + session factory.
Base est définie dans models.py — ne pas la redéfinir ici.
"""

import os
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool
from core.config import settings

# ── Engine async ──────────────────────────────────────────────────────────────
engine_kwargs: dict = {
    "echo": settings.DEBUG,
}

# disable pooling during tests to prevent "another operation is in progress"
if os.getenv("TESTING"):
    engine_kwargs["poolclass"] = NullPool

# additional connection params (only when not testing)
if not os.getenv("TESTING"):
    if "postgresql" in settings.DATABASE_URL or "asyncpg" in settings.DATABASE_URL:
        engine_kwargs["pool_size"] = 10
        engine_kwargs["max_overflow"] = 20
    elif "sqlite" in settings.DATABASE_URL:
        engine_kwargs["connect_args"] = {"timeout": 15}

engine = create_async_engine(settings.DATABASE_URL, **engine_kwargs)

# ensure PostgreSQL sessions use Tunisia timezone (UTC+1/2)
from sqlalchemy import event

@event.listens_for(engine.sync_engine, "connect")
def set_timezone(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("SET TIME ZONE 'Africa/Tunis'")
    cursor.close()

# ── Session factory ───────────────────────────────────────────────────────────
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


# ── FastAPI dependency ────────────────────────────────────────────────────────
async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
