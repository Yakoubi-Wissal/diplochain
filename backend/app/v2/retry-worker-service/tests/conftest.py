import sys
import pathlib
import pytest
import pytest_asyncio
import asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import StaticPool

# Setup paths
service_root = pathlib.Path(__file__).parent.parent
app_pkg = service_root / "app"
if str(app_pkg) not in sys.path:
    sys.path.insert(0, str(app_pkg))

# Standardize clearing for all microservices
to_del = [m for m in sys.modules if m.startswith(("main", "app.main"))]
for m in to_del:
    del sys.modules[m]

# Mock DATABASE_URL before importing app
import os
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"

import main
from main import app

# Use SQLite in-memory for testing
test_engine = create_async_engine(
    "sqlite+aiosqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
main.engine = test_engine

@pytest_asyncio.fixture(scope="session", autouse=True)
async def init_db():
    async with test_engine.begin() as conn:
        # Create the necessary table for the worker
        await conn.execute(text("""
            CREATE TABLE diplome_blockchain_ext (
                id_diplome INTEGER PRIMARY KEY,
                hash_sha256 TEXT,
                ipfs_cid TEXT,
                statut TEXT,
                blockchain_retry_count INTEGER DEFAULT 0
            )
        """))
    yield
    await test_engine.dispose()

from sqlalchemy import text

@pytest_asyncio.fixture
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
