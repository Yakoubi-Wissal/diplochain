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
from httpx import AsyncClient, ASGITransport
from fastapi import status

from app.main import app

@pytest.mark.asyncio
async def test_notification_operations():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        payload = {
            "user_id": 99,
            "type_notification": "EMAIL",
            "message": "Welcome to DiploChain!"
        }
        r = await client.post("/notifications/", json=payload)
        assert r.status_code == status.HTTP_201_CREATED
        assert r.json()["message"] == "Welcome to DiploChain!"

        r2 = await client.get("/notifications/user/99")
        assert r2.status_code == 200
        assert len(r2.json()) > 0
