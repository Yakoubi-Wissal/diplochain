import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

import pytest
from httpx import AsyncClient, ASGITransport
from fastapi import status

from app.main import app

@pytest.mark.asyncio
async def test_user_crud():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        payload = {"email": "foo@bar.com", "password": "secret"}
        r = await client.post("/users/", json=payload)
        assert r.status_code == status.HTTP_201_CREATED
        data = r.json()
        assert data["email"] == "foo@bar.com"
        uid = data["id_user"]

        r2 = await client.get(f"/users/{uid}")
        assert r2.status_code == 200
        assert r2.json()["id_user"] == uid

        r3 = await client.put(f"/users/{uid}", json={"status": "SUSPENDU"})
        assert r3.status_code == 200
        assert r3.json()["status"] == "SUSPENDU"
