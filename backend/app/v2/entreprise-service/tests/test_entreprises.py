from httpx import AsyncClient, ASGITransport
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

@pytest.mark.asyncio
async def test_entreprise_operations():
    unique_id = int(time.time()) % 1000000
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        payload = {
            "nom_entreprise": f"TechCorp_{unique_id}",
            "matricule_fiscale": f"MF_{unique_id}",
            "secteur_activite": "Technology",
            "adresse": "Test Address"
        }
        r = await client.post("/entreprises/", json=payload)
        if r.status_code not in [200, 201]:
            print(f"Error 422 details: {r.json()}")
        assert r.status_code in [200, 201]
        assert r.json()["nom_entreprise"] == payload["nom_entreprise"]

        r2 = await client.get("/entreprises/", params={"nom_entreprise": payload["nom_entreprise"]})
        assert r2.status_code == 200
        assert any(e["nom_entreprise"] == payload["nom_entreprise"] for e in r2.json())
async def test_entreprise_operations(client: AsyncClient):
    # Test Create
    payload = {
        "nom_entreprise": "TechCorp",
        "matricule_fiscale": "MF123",
        "secteur_activite": "Technology",
        "adresse": "Test Address"
    }
    response = await client.post("/", json=payload)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["nom_entreprise"] == "TechCorp"

    # Test List
    response = await client.get("/")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) >= 1
    assert any(e["nom_entreprise"] == "TechCorp" for e in response.json())
