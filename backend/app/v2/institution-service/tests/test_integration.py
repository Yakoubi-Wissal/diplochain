import pytest
from httpx import AsyncClient, ASGITransport
import time

# The app is imported via PYTHONPATH which points to 'app' directory
from main import app

@pytest.mark.asyncio
async def test_health(client):
    r = await client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "healthy"}

@pytest.mark.asyncio
async def test_create_institution(client):
    unique_id = int(time.time())
    inst_data = {
        "nom_institution": f"Test University {unique_id}",
        "email_institution": f"contact_{unique_id}@testuni.edu",
        "date_creation": "2026-01-01",
        "adresse": "123 Test St",
        "pays": "Tunisia"
    }
    # Router included at root, so use "/" instead of "/institutions/"
    response = await client.post("/", json=inst_data)
    assert response.status_code == 200
    data = response.json()
    assert data["nom_institution"] == inst_data["nom_institution"]
    assert "institution_id" in data
