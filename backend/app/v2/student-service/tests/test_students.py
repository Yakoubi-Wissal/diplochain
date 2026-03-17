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
async def test_student_operations():
    async with AsyncClient(app=app, base_url="http://test") as client:
        payload = {"etudiant_id": "S123", "nom": "Test", "prenom": "User"}
        r = await client.post("/students/", json=payload)
        assert r.status_code == status.HTTP_201_CREATED
        assert r.json()["etudiant_id"] == "S123"

        r2 = await client.get("/students/?nom=Test")
        assert r2.status_code == 200
        assert any(s["nom"] == "Test" for s in r2.json())
