import pytest
from httpx import AsyncClient
from fastapi import status

@pytest.mark.asyncio
async def test_diploma_crud():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        payload = {
            "titre": "D1",
            "mention": "A",
            "date_emission": "2025-01-01",
            "hash_sha256": "abc",
            "ipfs_cid": "cid123",
            "etudiant_id": "E1",
            "institution_id": 1,
            "uploaded_by": 1,
        }
        r = await client.post("/", json=payload)
        assert r.status_code == status.HTTP_200_OK
        data = r.json()
        assert data["titre"] == "D1"
        did = data["id_diplome"]

        r2 = await client.get(f"/{did}")
        assert r2.status_code == status.HTTP_200_OK
        assert r2.json()["id_diplome"] == did

        r3 = await client.post(f"/{did}/revoke")
        assert r3.status_code == status.HTTP_200_OK
        assert r3.json()["statut"] == "REVOQUE"
async def test_diploma_crud(client: AsyncClient):
    # Test Create
    payload = {
        "etudiant_id": "STUD001",
        "titre": "Master in Blockchain",
        "mention": "Tres Bien",
        "hash_sha256": "f0e4c2f76c58916ec258f246851bea091d14d4247a2fc3e18694461b1816e13b",
        "ipfs_cid": "QmXoypizjW3WknFiJnKLwHCnL72vedxjQkDDP1mXWo6uco",
        "institution_id": 1,
        "uploaded_by": 1,
        "specialite_id": "S1"
    }
    response = await client.post("/", json=payload)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["titre"] == "Master in Blockchain"
    diploma_id = data["id_diplome"]

    # Test Read
    response = await client.get(f"/{diploma_id}")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["titre"] == "Master in Blockchain"
