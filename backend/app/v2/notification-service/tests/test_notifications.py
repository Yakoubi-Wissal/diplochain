import pytest
from httpx import AsyncClient
from fastapi import status

@pytest.mark.asyncio
async def test_notification_operations(client: AsyncClient):
    payload = {
        "user_id": 99,
        "type_notification": "EMAIL",
        "message": "Welcome to DiploChain!"
    }
    r = await client.post("/", json=payload)
    assert r.status_code == status.HTTP_201_CREATED
    data = r.json()
    assert data["message"] == payload["message"]
    assert "id" in data
