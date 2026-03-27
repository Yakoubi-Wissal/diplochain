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
