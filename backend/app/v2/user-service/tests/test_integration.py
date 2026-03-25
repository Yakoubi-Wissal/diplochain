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

def test_auth_flow():
    # 1. Register a user with a hashed password (manual inject for test)
    # Actually, we should test the registration endpoint if it hashes passwords
    pass

@pytest.mark.asyncio
async def test_create_user():
    unique_id = int(time.time())
    user_data = {
        "username": f"testuser_{unique_id}",
        "email": f"test_{unique_id}@example.com",
        "status": "ACTIVE",
        "revoked": False,
        "expired": False,
        "password": "password123"
    }
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/users/", json=user_data)
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["email"] == user_data["email"]
        assert "id_user" in data

@pytest.mark.asyncio
async def test_list_users():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test", follow_redirects=True) as client:
        # User router is prefixed with /users
        # @router.get("/all", response_model=List[UserRead])
        # Testing if it's the 'status' param that's causing 422
        response = await client.get("/users/all")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

@pytest.mark.asyncio
async def test_create_role():
    unique_id = int(time.time())
    role_data = {
        "code": f"TEST_ROLE_{unique_id}",
        "label_role": "Test Role Label",
        "id_cursus": 1
    }
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/roles/", json=role_data)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == role_data["code"]
        assert "id_role" in data
