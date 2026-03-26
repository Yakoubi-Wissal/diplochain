import pytest
from fastapi import status
import time

@pytest.mark.asyncio
async def test_entreprise_operations(client):
    unique_id = int(time.time()) % 1000000
    payload = {
        "nom_entreprise": f"TechCorp_{unique_id}",
        "matricule_fiscale": f"MF_{unique_id}",
        "secteur_activite": "Technology",
        "adresse": "Test Address"
    }
    r = await client.post("/api/", json=payload)
    assert r.status_code in [200, 201]
    data = r.json()
    assert data["nom_entreprise"] == payload["nom_entreprise"]

    r2 = await client.get("/api/", params={"nom_entreprise": payload["nom_entreprise"]})
    assert r2.status_code == 200
    results = r2.json()
    assert isinstance(results, list)
    assert any(e["nom_entreprise"] == payload["nom_entreprise"] for e in results)
