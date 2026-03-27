import pytest
from httpx import AsyncClient
from fastapi import status

@pytest.mark.asyncio
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
