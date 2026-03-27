import pytest
from httpx import AsyncClient
from sqlalchemy import text
import main

@pytest.mark.asyncio
async def test_health(client: AsyncClient):
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

@pytest.mark.asyncio
async def test_worker_trigger(client: AsyncClient):
    # Seed data
    async with main.engine.begin() as conn:
        await conn.execute(text(
            "INSERT INTO diplome_blockchain_ext (id_diplome, hash_sha256, ipfs_cid, statut, blockchain_retry_count) "
            "VALUES (1, 'hash1', 'cid1', 'PENDING_BLOCKCHAIN', 0)"
        ))

    # Trigger worker (it will fail to contact blockchain-service but should increment retry count)
    response = await client.post("/worker/trigger")
    assert response.status_code == 200

    # Check if retry count incremented
    async with main.engine.begin() as conn:
        result = await conn.execute(text("SELECT blockchain_retry_count FROM diplome_blockchain_ext WHERE id_diplome = 1"))
        row = result.fetchone()
        assert row.blockchain_retry_count == 1
