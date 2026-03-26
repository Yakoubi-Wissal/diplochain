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

@pytest.mark.asyncio
async def test_blockchain_endpoints():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        payload = {"id_diplome": 1, "titre": "T", "hash_sha256": "h", "created_at": "2023-01-01T00:00:00", "updated_at": "2023-01-01T00:00:00"}
        r = await client.post("/diplome", json=payload)
        assert r.status_code == status.HTTP_200_OK
        assert r.json()["id_diplome"] == 1

        r2 = await client.get("/diplome/1")
        assert r2.status_code == status.HTTP_200_OK
