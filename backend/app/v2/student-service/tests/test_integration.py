import pytest
import httpx
from fastapi import status
import time

BASE_URL = "http://localhost:8000"

@pytest.mark.asyncio
async def test_health():
    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.get(f"{BASE_URL}/health")
        assert response.status_code == 200

@pytest.mark.asyncio
async def test_create_student():
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
    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.post(f"{BASE_URL}/students/", json=student_data)
        if response.status_code != 200:
            print(f"Error 422 details: {response.json()}")
        assert response.status_code == 200
        data = response.json()
        assert data["etudiant_id"] == student_data["etudiant_id"]
