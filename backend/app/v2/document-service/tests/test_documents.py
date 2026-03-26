import pytest
from fastapi import status

@pytest.mark.asyncio
async def test_rapport_operations(client):
    # Testing GET /api/ which should return a list of rapports
    r = await client.get("/api/")
    assert r.status_code == status.HTTP_200_OK
    assert isinstance(r.json(), list)

    # Test creating a rapport
    payload = {
        "nom_documents": "Test Doc",
        "id_langue": 1,
        "id_type_impression": 1,
        "id_annee": 2025,
        "etat": True,
        "code_rapport": "R-123"
    }
    r2 = await client.post("/api/", json=payload)
    assert r2.status_code == status.HTTP_200_OK
    assert r2.json()["code_rapport"] == "R-123"
