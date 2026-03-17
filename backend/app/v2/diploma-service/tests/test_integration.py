import pytest
import httpx
from fastapi import status
import uuid

BASE_URL = "http://localhost:8000"

@pytest.mark.asyncio
async def test_health():
    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.get(f"{BASE_URL}/diplomas/")
        assert response.status_code == 200 or response.status_code == 404

@pytest.mark.asyncio
async def test_create_diploma():
    diploma_data = {
        "id_diplome": str(uuid.uuid4()),
        "titre": "Master in Blockchain",
        "mention": "Tres Bien",
        "date_emission": "2023-12-01",
        "annee_promotion": "2023",
        "statut": "VALIDE",
        "etudiant_id": "STUD001",
        "institution_id": 1,
        "specialite_id": 1
    }
    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.post(f"{BASE_URL}/diplomas/", json=diploma_data)
        assert response.status_code == 200
        data = response.json()
        assert data["titre"] == diploma_data["titre"]
