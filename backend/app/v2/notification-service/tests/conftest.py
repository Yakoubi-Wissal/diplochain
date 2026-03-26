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
    db_file = "./test_notification_service.db"
    if os.path.exists(db_file):
        try: os.remove(db_file)
        except: pass
