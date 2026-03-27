import pytest_asyncio
import sys
import pathlib
import os

# Absolute isolation: purge ALL modules that might collide
for name in list(sys.modules):
    if any(p in name for p in ["routers", "core", "main", "app"]):
        del sys.modules[name]

# Set up paths for this specific service
service_root = pathlib.Path(__file__).parent.parent
app_pkg = service_root / "app"

# Remove any other microservice paths from sys.path
sys.path = [p for p in sys.path if "backend/app/v2" not in p]

if str(app_pkg) not in sys.path:
    sys.path.insert(0, str(app_pkg))
if str(service_root) not in sys.path:
    sys.path.insert(0, str(service_root))

from core.database import engine, Base
from main import app

@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_db():
    if True:
        import core.models
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    # Cleanup
    db_file = "./test_entreprise_service.db"
    if os.path.exists(db_file):
        try: os.remove(db_file)
        except: pass
import pytest
import pytest_asyncio
import asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.pool import StaticPool

# Setup paths
service_root = pathlib.Path(__file__).parent.parent
app_pkg = service_root / "app"
if str(app_pkg) not in sys.path:
    sys.path.insert(0, str(app_pkg))

# Standardize clearing for all microservices
to_del = [m for m in sys.modules if m.startswith(("core", "routers", "models", "main", "schemas"))]
for m in to_del:
    del sys.modules[m]

import core.database
import core.models
from main import app

# Use SQLite in-memory with StaticPool for test isolation but session persistence
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"
engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

# Monkeypatch the database module
core.database.engine = engine
core.database.AsyncSessionLocal = TestingSessionLocal

async def override_get_db():
    async with TestingSessionLocal() as session:
        yield session

app.dependency_overrides[core.database.get_db] = override_get_db
import routers.entreprises
app.dependency_overrides[routers.entreprises.get_db] = override_get_db

@pytest_asyncio.fixture(scope="session", autouse=True)
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(core.models.Base.metadata.create_all)
    yield
    await engine.dispose()

@pytest_asyncio.fixture
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
