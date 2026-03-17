import pytest
import httpx
from fastapi import status
import time

BASE_URL = "http://localhost:8000"

@pytest.mark.asyncio
async def test_health():
    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.get(f"{BASE_URL}/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}

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
    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.post(f"{BASE_URL}/users/", json=user_data)
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["email"] == user_data["email"]
        assert "id_user" in data

@pytest.mark.asyncio
async def test_list_users():
    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.get(f"{BASE_URL}/users/")
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
    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.post(f"{BASE_URL}/roles/", json=role_data)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == role_data["code"]
        assert "id_role" in data
