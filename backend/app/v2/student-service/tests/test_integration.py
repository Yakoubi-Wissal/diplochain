import pytest
import httpx
from fastapi import status
import uuid
from app.main import app
from core.database import Base, engine
import pytest_asyncio

@pytest_asyncio.fixture(autouse=True)
async def setup_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.mark.asyncio
async def test_health_integration():
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/health")
        assert response.status_code in [200, 201]

@pytest.mark.asyncio
async def test_create_student():
from httpx import AsyncClient, ASGITransport
from main import app
import time

@pytest.mark.asyncio
async def test_health(client: AsyncClient):
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

@pytest.mark.asyncio
async def test_create_student_integration(client: AsyncClient):
    unique_id = int(time.time() * 1000) % 1000000
    student_data = {
        "etudiant_id": "S123",
        "nom": "Doe",
        "prenom": "John",
        "email_etudiant": "john@test.com",
        "date_naissance": "2000-01-01",
        "sexe": "M",
        "lieu_nais_et": "Tunis"
    }
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/", json=student_data)
        assert response.status_code == 201
        data = response.json()
        assert data["etudiant_id"] == student_data["etudiant_id"]
    response = await client.post("/", json=student_data)
    assert response.status_code == 200
    data = response.json()
    assert data["etudiant_id"] == student_data["etudiant_id"]
