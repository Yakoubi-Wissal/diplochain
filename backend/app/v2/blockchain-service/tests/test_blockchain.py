import pytest
from httpx import AsyncClient
from fastapi import status

@pytest.mark.asyncio
async def test_blockchain_endpoints(client: AsyncClient):
    # Test Create
    payload = {
        "id_diplome": 1,
        "titre": "Engineer Degree",
        "hash_sha256": "f0e4c2f76c58916ec258f246851bea091d14d4247a2fc3e18694461b1816e13b"
    }
    response = await client.post("/blockchain/diplome", json=payload)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id_diplome"] == 1
    assert data["titre"] == "Engineer Degree"

    # Test Read
    response = await client.get("/blockchain/diplome/1")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["titre"] == "Engineer Degree"

    # Test Audit
    response = await client.get("/blockchain/audit/ledger")
    assert response.status_code == status.HTTP_200_OK
    assert "total_records" in response.json()
    assert response.json()["total_records"] >= 1
