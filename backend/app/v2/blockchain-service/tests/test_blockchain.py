import pytest
from httpx import AsyncClient, ASGITransport
from fastapi import status

# The app is imported via PYTHONPATH which should point to the 'app' directory
from main import app

@pytest.mark.asyncio
async def test_blockchain_endpoints(client):
    # Testing the POST endpoint defined in routers/blockchain.py
    # The router is included in main.py without a prefix: app.include_router(blockchain.router, prefix="")
    # The endpoint itself is @router.post("/diplome")
    payload = {
        "id_diplome": 1,
        "titre": "T",
        "hash_sha256": "h" * 64, # Meet schema/audit requirements
        "institution_id": 1,
        "date_inscription": "2025-01-01"
    }
    r = await client.post("/diplome", json=payload)
    assert r.status_code == status.HTTP_200_OK
    assert r.json()["id_diplome"] == 1

    r2 = await client.get("/diplome/1")
    assert r2.status_code == status.HTTP_200_OK
    assert r2.json()["id_diplome"] == 1

    # Test audit endpoint
    r3 = await client.get("/audit/ledger")
    assert r3.status_code == status.HTTP_200_OK
    assert "integrity_score" in r3.json()
