import pytest
from httpx import AsyncClient, ASGITransport
from main import app
import time

@pytest.mark.asyncio
async def test_health(client: AsyncClient):
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

@pytest.mark.asyncio
async def test_create_student_integration(client: AsyncClient):
    unique_id = int(time.time() * 1000) % 1000000
    student_data = {
        "etudiant_id": f"S{unique_id}",
        "nom": "Doe",
        "prenom": "John",
        "email_etudiant": f"john_{unique_id}@test.com",
        "date_naissance": "2000-01-01",
        "sexe": "M",
        "lieu_nais_et": "Tunis"
    }
    response = await client.post("/", json=student_data)
    assert response.status_code == 200
    data = response.json()
    assert data["etudiant_id"] == student_data["etudiant_id"]
