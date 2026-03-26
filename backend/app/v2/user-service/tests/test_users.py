import sys, pathlib
service_root = pathlib.Path(__file__).parent.parent
app_pkg = service_root / "app"
if str(app_pkg) not in sys.path:
    sys.path.insert(0, str(app_pkg))

import pytest
import uuid
from httpx import AsyncClient, ASGITransport
from fastapi import status

from app.main import app

@pytest.mark.asyncio
async def test_user_crud():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test", follow_redirects=True) as client:
        email = f"user_{uuid.uuid4().hex[:8]}@test.com"
        payload = {"email": email, "password": "secret", "username": "testuser"}
        r = await client.post("/users/", json=payload)
        assert r.status_code == status.HTTP_201_CREATED
        data = r.json()
        assert data["email"] == email
        uid = data["id_user"]

        r2 = await client.get(f"/users/{uid}")
        assert r2.status_code == 200
        assert r2.json()["email"] == email

        payload_upd = {"username": "newname"}
        r3 = await client.put(f"/users/{uid}", json=payload_upd)
        assert r3.status_code == 200
        assert r3.json()["username"] == "newname"
