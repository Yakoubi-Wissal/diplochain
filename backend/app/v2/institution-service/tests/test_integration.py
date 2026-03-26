from httpx import AsyncClient, ASGITransport
import pytest
import httpx
from fastapi import status
import time

BASE_URL = "http://localhost:8000"

@pytest.mark.asyncio
async def test_health():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/health")
        assert response.status_code in [200, 201]

@pytest.mark.asyncio
async def test_create_institution():
    unique_id = int(time.time())
    inst_data = {
        "nom_institution": f"Test University {unique_id}",
        "email_institution": f"contact_{unique_id}@testuni.edu",
        "date_creation": "2026-01-01",
        "adresse": "123 Test St",
        "pays": "Tunisia"
    }
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/institutions/", json=inst_data)
        if response.status_code != 200:
            print(f"Error 422 details: {response.json()}")
        assert response.status_code in [200, 201] # Based on institutions.py
        data = response.json()
        assert data["nom_institution"] == inst_data["nom_institution"]
        assert "institution_id" in data
