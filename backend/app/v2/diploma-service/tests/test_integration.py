import pytest
import httpx
from fastapi import status
import uuid
from app.main import app

@pytest.mark.asyncio
async def test_health_integration():
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/")
        assert response.status_code in [200, 201]

@pytest.mark.asyncio
async def test_create_diploma_integration():
    diploma_data = {
        "etudiant_id": "STUD001",
        "titre": "Master in Blockchain",
        "mention": "Tres Bien",
        "date_emission": "2023-12-01",
        "annee_promotion": "2023",
        "hash_sha256": str(uuid.uuid4()),
        "ipfs_cid": "cid123",
        "institution_id": 1,
        "uploaded_by": 1
    }
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/", json=diploma_data)
        assert response.status_code in [200, 201]
        data = response.json()
        assert data["titre"] == diploma_data["titre"]
