import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_health(client: AsyncClient):
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

@pytest.mark.asyncio
async def test_fix_trigger(client: AsyncClient):
    response = await client.post("/fix/test-service")
    assert response.status_code == 200
    assert response.json()["status"] == "triggered"
