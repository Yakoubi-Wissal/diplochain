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
async def test_create_student(client):
    unique_id = int(time.time()) % 1000000
    student_data = {
        "etudiant_id": f"S{unique_id}",
        "nom": "Doe",
        "prenom": "John",
        "email_etudiant": f"john_{unique_id}@test.com",
        "date_naissance": "2000-01-01",
        "sexe": "M",
        "lieu_nais_et": "Tunis"
    }
    # Router included at root, so use "/" instead of "/students/"
    response = await client.post("/", json=student_data)
    assert response.status_code == 200
    data = response.json()
    assert data["etudiant_id"] == student_data["etudiant_id"]
