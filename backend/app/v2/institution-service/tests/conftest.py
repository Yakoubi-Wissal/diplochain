import sys
import pathlib
import pytest
import asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

# Put service root/app on sys.path and clear previous modules
service_root = pathlib.Path(__file__).parent.parent
app_pkg = service_root / "app"
sys.path.insert(0, str(app_pkg))

for name in list(sys.modules):
    if name in ["routers", "core", "main"] or name.startswith(("routers.", "core.")):
        del sys.modules[name]

# Import using the same style as the app
from core.database import Base
import core.models
from main import app
import routers.institutions as inst_router

# Use a persistent file for SQLite during tests to avoid in-memory isolation issues
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test_institutions.db"

test_engine = create_async_engine(TEST_DATABASE_URL, echo=False, future=True)
TestAsyncSessionLocal = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False
)

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session", autouse=True)
async def create_test_db():
    import os
    if os.path.exists("./test_institutions.db"):
        os.remove("./test_institutions.db")

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    if os.path.exists("./test_institutions.db"):
        os.remove("./test_institutions.db")

async def override_get_db():
    async with TestAsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

# OVERRIDE THE LOCAL get_db in the router module
app.dependency_overrides[inst_router.get_db] = override_get_db

# Patch app lifespan to do nothing during tests
from contextlib import asynccontextmanager
@asynccontextmanager
async def mock_lifespan(app):
    yield
app.router.lifespan_context = mock_lifespan

@pytest.fixture
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac

@pytest.fixture
async def db_session():
    async with TestAsyncSessionLocal() as session:
        yield session
