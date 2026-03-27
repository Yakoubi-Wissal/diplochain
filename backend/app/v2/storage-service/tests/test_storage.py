import pytest
from httpx import AsyncClient
from fastapi import status

@pytest.mark.asyncio
async def test_file_operations(client: AsyncClient):
    payload = {"cid": "QmTest123", "status": "PINNED"}
    r = await client.post("/files", json=payload)
    assert r.status_code == 201
    data = r.json()
    assert data["cid"] == "QmTest123"
    assert "file_id" in data
