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
    if False:
        import core.models
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    # Cleanup
    db_file = "./test_api_gateway.db"
    if os.path.exists(db_file):
        try: os.remove(db_file)
        except: pass
import sys
import pathlib
import pytest
import pytest_asyncio
import asyncio
from httpx import AsyncClient, ASGITransport

# Setup paths
service_root = pathlib.Path(__file__).parent.parent
app_pkg = service_root / "app"
if str(app_pkg) not in sys.path:
    sys.path.insert(0, str(app_pkg))

# Standardize clearing for all microservices
to_del = [m for m in sys.modules if m.startswith(("main", "app.main"))]
for m in to_del:
    del sys.modules[m]

from main import app

@pytest_asyncio.fixture
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
