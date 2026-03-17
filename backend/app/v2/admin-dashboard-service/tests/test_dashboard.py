import sys, pathlib
service_root = pathlib.Path(__file__).parent.parent
app_folder = service_root / "app"
for p in (service_root, app_folder):
    sp = str(p)
    if sp not in sys.path:
        sys.path.insert(0, sp)
for name in list(sys.modules):
    if name == "routers" or name.startswith("routers.") or name == "core" or name.startswith("core."):
        del sys.modules[name]

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from httpx import AsyncClient

# Mock the DB init before importing the app
with patch("core.database.init_db", new=AsyncMock()):
    from app.main import app

# Override get_db to return a mocked session
async def mock_get_db():
    mock_session = AsyncMock()
    result_mock = MagicMock()
    result_mock.scalars.return_value.all.return_value = []
    mock_session.execute = AsyncMock(return_value=result_mock)
    yield mock_session

from routers.dashboard import get_db
app.dependency_overrides[get_db] = mock_get_db

@pytest.mark.asyncio
async def test_health():
    async with AsyncClient(app=app, base_url="http://test") as client:
        r = await client.get("/health")
        assert r.status_code == 200
        assert r.json() == {"status": "ok"}

@pytest.mark.asyncio
async def test_admin_diplomas():
    async with AsyncClient(app=app, base_url="http://test") as client:
        r = await client.get("/api/admin/diplomas")
        assert r.status_code == 200

@pytest.mark.asyncio
async def test_admin_students():
    async with AsyncClient(app=app, base_url="http://test") as client:
        r = await client.get("/api/admin/students")
        assert r.status_code == 200

@pytest.mark.asyncio
async def test_admin_institutions():
    async with AsyncClient(app=app, base_url="http://test") as client:
        r = await client.get("/api/admin/institutions")
        assert r.status_code == 200
