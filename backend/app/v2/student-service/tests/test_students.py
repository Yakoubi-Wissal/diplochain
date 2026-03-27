import pytest
from httpx import AsyncClient
from fastapi import status

@pytest.mark.asyncio
async def test_student_operations(client: AsyncClient):
    # Test Create - removing trailing slash to avoid 307
    payload = {"etudiant_id": "S123", "nom": "Test", "prenom": "User"}
    response = await client.post("/", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["etudiant_id"] == "S123"

    # Test Read
    response = await client.get("/S123")
    assert response.status_code == 200
    assert response.json()["nom"] == "Test"

    # Test Search
    response = await client.get("/search?nom=Test")
    assert response.status_code == 200
    assert len(response.json()) >= 1
