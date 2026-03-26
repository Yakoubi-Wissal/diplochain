import pytest
import httpx
from httpx import AsyncClient, ASGITransport
from app.main import app
import time
import uuid
from core.database import Base, engine

@pytest.mark.asyncio
async def test_health():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/health")
        assert response.status_code == 200

@pytest.mark.asyncio
async def test_create_user():
    unique_id = uuid.uuid4().hex[:8]
    user_data = {
        "username": f"testuser_{unique_id}",
        "email": f"test_int_{unique_id}@example.com",
        "status": "ACTIVE",
        "password": "password123"
    }
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/users/", json=user_data)
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == user_data["email"]

@pytest.mark.asyncio
async def test_list_users():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/users/all")
        assert response.status_code == 200
        assert isinstance(response.json(), list)
