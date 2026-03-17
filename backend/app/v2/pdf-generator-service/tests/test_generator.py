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
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_health():
    async with AsyncClient(app=app, base_url="http://test") as client:
        r = await client.get("/health")
        assert r.status_code == 200
        assert r.json() == {"status": "healthy"}

@pytest.mark.asyncio
async def test_generate_diploma():
    async with AsyncClient(app=app, base_url="http://test") as client:
        payload = {
            "template_id": "template_uuid_123",
            "student": {
                "nom": "Ben Ali",
                "prenom": "Mohamed",
                "date_naissance": "1998-03-15",
                "numero_etudiant": "ETU-2024-001"
            },
            "diploma": {
                "titre": "Master HQ",
                "mention": "TB",
                "date_emission": "2024-06-15",
                "annee_promotion": "2024"
            },
            "institution": {
                "nom": "Université",
                "logo_url": "url",
                "responsable": "Admin"
            }
        }
        r = await client.post("/generate-diploma", json=payload)
        assert r.status_code == 200
        assert r.headers["content-type"] == "application/pdf"
        assert len(r.content) > 0 # PDF bytes returned
