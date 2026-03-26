import pytest
from httpx import AsyncClient
from fastapi import status

@pytest.mark.asyncio
async def test_student_operations(client: AsyncClient, db_session):
    payload = {
        "etudiant_id": "S123",
        "nom": "Test",
        "prenom": "User",
        "email_etudiant": "test@student.com",
        "date_naissance": "2000-01-01"
    }
    r = await client.post("/", json=payload)
    assert r.status_code == status.HTTP_200_OK
    assert r.json()["etudiant_id"] == "S123"

    r2 = await client.get("/search?nom=Test")
    assert r2.status_code == 200
    assert any(s["nom"] == "Test" for s in r2.json())
