import pytest
from httpx import AsyncClient
from fastapi import status

@pytest.mark.asyncio
@pytest.mark.asyncio
async def test_health(client: AsyncClient):
    r = await client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "healthy"}
