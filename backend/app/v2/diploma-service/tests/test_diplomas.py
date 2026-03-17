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
from httpx import AsyncClient
from fastapi import status

from app.main import app

@pytest.mark.asyncio
async def test_diploma_crud():
    async with AsyncClient(app=app, base_url="http://test") as client:
        payload = {
            "titre": "D1",
            "mention": "A",
            "date_emission": "2025-01-01",
            "hash_sha256": "abc",
            "ipfs_cid": "cid123",
            "etudiant_id": "E1",
            "institution_id": "I1",
            "uploaded_by": "U1",
        }
        r = await client.post("/diplomas/", json=payload)
        assert r.status_code == status.HTTP_200_OK
        data = r.json()
        assert data["titre"] == "D1"
        did = data["id"]

        r2 = await client.get(f"/diplomas/{did}")
        assert r2.status_code == status.HTTP_200_OK
        assert r2.json()["id"] == did

        r3 = await client.post(f"/diplomas/{did}/revoke")
        assert r3.status_code == status.HTTP_200_OK
        assert r3.json()["statut"] == "REVOQUE"
