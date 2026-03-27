import pytest
from httpx import AsyncClient
from fastapi import status

@pytest.mark.asyncio
async def test_blockchain_endpoints():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        payload = {"id_diplome": 1, "titre": "T", "hash_sha256": "h", "created_at": "2023-01-01T00:00:00", "updated_at": "2023-01-01T00:00:00"}
        r = await client.post("/diplome", json=payload)
        assert r.status_code == status.HTTP_200_OK
        assert r.json()["id_diplome"] == 1

        r2 = await client.get("/diplome/1")
        assert r2.status_code == status.HTTP_200_OK
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
