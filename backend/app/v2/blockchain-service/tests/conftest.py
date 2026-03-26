import sys
import pathlib
import pytest
import asyncio
import os
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

# Standardize path to service root/app
service_root = pathlib.Path(__file__).parent.parent
app_dir = service_root / "app"
if str(app_dir) not in sys.path:
    sys.path.insert(0, str(app_dir))

# Clear existing modules to ensure clean imports from app_dir
for name in list(sys.modules):
    if name in ["routers", "core", "main"] or name.startswith(("routers.", "core.")):
        del sys.modules[name]

# Import using app-relative names
from core.database import Base, get_db as db_get_db
import core.models as models_module
from main import app
from routers.blockchain import get_db as blockchain_get_db

# Use a persistent file for SQLite
TEST_DB_FILE = "./test_blockchain.db"
TEST_DATABASE_URL = f"sqlite+aiosqlite:///{TEST_DB_FILE}"

test_engine = create_async_engine(TEST_DATABASE_URL, echo=False, future=True)
TestAsyncSessionLocal = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False
)

@pytest.fixture(scope="session", autouse=True)
async def create_test_db():
    if os.path.exists(TEST_DB_FILE):
        os.remove(TEST_DB_FILE)

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    if os.path.exists(TEST_DB_FILE):
        os.remove(TEST_DB_FILE)

async def override_get_db():
    async with TestAsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

# OVERRIDE the dependencies
app.dependency_overrides[blockchain_get_db] = override_get_db
app.dependency_overrides[db_get_db] = override_get_db

from contextlib import asynccontextmanager
@asynccontextmanager
async def mock_lifespan(app):
    yield
app.router.lifespan_context = mock_lifespan

@pytest.fixture
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
