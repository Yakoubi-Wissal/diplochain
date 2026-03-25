import sys, pathlib
# adjust path so this service's root and its app package are first
service_root = pathlib.Path(__file__).parent.parent
app_folder = service_root / "app"
for p in (service_root, app_folder):
    sp = str(p)
    if sp not in sys.path:
        sys.path.insert(0, sp)
# remove conflicting modules from earlier services
for name in list(sys.modules):
    if name == "routers" or name.startswith("routers.") or name == "core" or name.startswith("core."):
        del sys.modules[name]

import pytest
from httpx import AsyncClient, ASGITransport
from fastapi import status

from app.main import app
from core.database import engine, Base

@pytest.mark.asyncio
async def test_health_and_metrics():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        r = await client.get("/health")
        assert r.status_code == status.HTTP_200_OK

        r2 = await client.get("/metrics/daily")
        assert r2.status_code == status.HTTP_200_OK

        r3 = await client.get("/metrics/realtime")
        assert r3.status_code == 200
        assert "stability_score" in r3.json()
