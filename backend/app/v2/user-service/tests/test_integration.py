import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

import pytest
import httpx
from httpx import AsyncClient, ASGITransport
from fastapi import status
import time

from app.main import app
from core.database import engine, Base

@pytest.mark.asyncio
async def test_health():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}

@pytest.mark.asyncio
async def test_create_user():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    unique_id = int(time.time())
    user_data = {
        "username": f"testuser_{unique_id}",
        "email": f"test_int_{unique_id}@example.com",
        "status": "ACTIVE",
        "revoked": False,
        "expired": False,
        "password": "password123"
    }
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/", json=user_data)
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["email"] == user_data["email"]
        assert "id_user" in data

@pytest.mark.asyncio
async def test_list_users():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/all")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

@pytest.mark.asyncio
async def test_create_role():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    unique_id = int(time.time())
    role_data = {
        "code": f"TEST_ROLE_INT_{unique_id}",
        "label_role": "Test Role Label",
        "id_cursus": 1
    }
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/roles/", json=role_data)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == role_data["code"]
        assert "id_role" in data
