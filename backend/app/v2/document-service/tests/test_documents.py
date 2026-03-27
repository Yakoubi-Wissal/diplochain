import pytest
from httpx import AsyncClient
from fastapi import status

@pytest.mark.asyncio
async def test_rapport_operations(client: AsyncClient):
    # Test Create
    payload = {
        "nom_documents": "Report 1",
        "id_langue": 1,
        "id_type_impression": 1,
        "id_annee": 2025,
        "etat": True,
        "code_rapport": "R001"
    }
    r = await client.post("/", json=payload)
    assert r.status_code == status.HTTP_201_CREATED
    data = r.json()
    assert data["nom_documents"] == payload["nom_documents"]
    assert "id_rapport" in data
