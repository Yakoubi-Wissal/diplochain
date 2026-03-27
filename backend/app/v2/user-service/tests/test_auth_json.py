import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

import pytest
import uuid
from httpx import AsyncClient, ASGITransport
from fastapi import status

from app.main import app
from core.database import engine, Base

@pytest.mark.asyncio
async def test_login_json_flow():
    """
    Vérifie que le flux de connexion JSON (email/password) fonctionne correctement
    et ne renvoie pas d'erreur 422.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # 1. Créer un utilisateur pour le test
        email = f"test_login_{uuid.uuid4().hex[:8]}@test.com"
        password = "testpassword123"
        user_payload = {"email": email, "password": password, "status": "ACTIVE"}

        create_resp = await client.post("/", json=user_payload)
        assert create_resp.status_code == status.HTTP_201_CREATED

        # 2. Tenter une connexion avec JSON
        login_payload = {"email": email, "password": password}
        login_resp = await client.post("/auth/login", json=login_payload)

        # On s'attend à un 200 OK avec un access_token
        assert login_resp.status_code == 200
        data = login_resp.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

@pytest.mark.asyncio
async def test_login_invalid_credentials():
    """
    Vérifie qu'une tentative de connexion avec de mauvais identifiants renvoie 401
    et non 422 (erreur de validation de schéma).
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        login_payload = {"email": "nonexistent@test.com", "password": "wrongpassword"}
        login_resp = await client.post("/auth/login", json=login_payload)

        assert login_resp.status_code == 401
        assert "incorrect" in login_resp.json()["detail"]
