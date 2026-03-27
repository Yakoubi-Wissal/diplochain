import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_health_integration(client: AsyncClient):
    response = await client.get("/health")
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_create_diploma_integration(client: AsyncClient):
    diploma_data = {
        "etudiant_id": "STUD002",
        "titre": "Bachelor in CS",
        "mention": "Bien",
        "hash_sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        "ipfs_cid": "QmYwAPJzv5CZsnAQCte71V3Hn7m5KuW4b2sJnY985WJ66p",
        "institution_id": 1,
        "uploaded_by": 1,
        "specialite_id": "S2"
    }
    response = await client.post("/", json=diploma_data)
    assert response.status_code == 200
    assert response.json()["titre"] == "Bachelor in CS"
