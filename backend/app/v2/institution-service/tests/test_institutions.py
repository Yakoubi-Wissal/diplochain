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

from app.main import app  # assuming main imports routers

@pytest.mark.asyncio
async def test_create_and_get_institution(monkeypatch):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # create
        payload = {
            "nom_institution": "Test Uni",
            "email_institution": "contact@test.edu",
            "date_creation": "2024-01-01"
        }
        resp = await client.post("/institutions/", json=payload)
        assert resp.status_code == status.HTTP_201_CREATED
        data = resp.json()
        assert data["nom_institution"] == "Test Uni"
        inst_id = data["institution_id"]

        # retrieve
        resp2 = await client.get(f"/institutions/{inst_id}")
        assert resp2.status_code == status.HTTP_200_OK
        assert resp2.json()["institution_id"] == inst_id

@pytest.mark.asyncio
async def test_list_institutions_filter():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/institutions/?active=true")
        assert resp.status_code == status.HTTP_200_OK
