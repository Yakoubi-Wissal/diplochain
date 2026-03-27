import pytest
from httpx import AsyncClient
from fastapi import status

@pytest.mark.asyncio
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
