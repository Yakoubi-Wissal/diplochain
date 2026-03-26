import pytest
from httpx import AsyncClient
from fastapi import status

@pytest.mark.asyncio
async def test_health(client: AsyncClient):
    r = await client.get("/health")
    assert r.status_code in [200, 201]
    assert r.json() == {"status": "healthy"}
