import pytest
from httpx import AsyncClient, ASGITransport
import uuid

# The app is imported via PYTHONPATH which points to 'app' directory
from main import app

@pytest.mark.asyncio
async def test_health(client):
    r = await client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "healthy"}

@pytest.mark.asyncio
async def test_create_diploma(client):
    unique_id = uuid.uuid4().hex[:8]
    diploma_data = {
        "etudiant_id": f"STUD_{unique_id}",
        "session_diplome": "Principale",
        "id_annexe": 1,
        "num_diplome": int(uuid.uuid4().int % 1000000),
        "date_diplome": "2023-12-01",
        "date_liv_diplome": "2023-12-01",
        "titre": f"Master in Blockchain {unique_id}",
        "mention": "Tres Bien",
        "date_emission": "2023-12-01",
        "annee_promotion": "2023",
        "hash_sha256": hashlib.sha256(unique_id.encode()).hexdigest(),
        "ipfs_cid": f"cid_{unique_id}",
        "statut": "ORIGINAL",
        "generation_mode": "UPLOAD",
        "template_id": 1,
        "institution_id": 1,
        "specialite_id": f"SPEC_{unique_id}",
        "uploaded_by": 1
    }
    # Router included at root, so use "/" instead of "/diplomas/"
    response = await client.post("/", json=diploma_data)
    assert response.status_code == 200
    data = response.json()
    assert data["titre"] == diploma_data["titre"]

import hashlib
