import sys
import pathlib
import pytest
import asyncio
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.pool import StaticPool

# Put service root/app on sys.path
service_root = pathlib.Path(__file__).parent.parent
app_pkg = service_root / "app"
if str(app_pkg) not in sys.path:
    sys.path.insert(0, str(app_pkg))

# remove conflicting modules
for name in list(sys.modules):
    if name in ["routers", "core"] or name.startswith(("routers.", "core.")):
        del sys.modules[name]

from core.database import Base
from main import app
import routers.analytics as analytics_router

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=False,
    future=True,
    poolclass=StaticPool
)
TestAsyncSessionLocal = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False
)

@pytest_asyncio.fixture(autouse=True)
async def create_test_db():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

async def override_get_db():
    async with TestAsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

app.dependency_overrides[analytics_router.get_db] = override_get_db

@pytest_asyncio.fixture
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac

@pytest_asyncio.fixture
async def db_session():
    async with TestAsyncSessionLocal() as session:
        yield session
