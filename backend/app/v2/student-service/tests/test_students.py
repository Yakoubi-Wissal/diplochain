import sys, pathlib
service_root = pathlib.Path(__file__).parent.parent
app_pkg = service_root / "app"
if str(app_pkg) not in sys.path:
    sys.path.insert(0, str(app_pkg))

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from fastapi import status

from main import app
from core.database import Base, engine

@pytest_asyncio.fixture(autouse=True)
async def setup_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.mark.asyncio
async def test_student_operations():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        payload = {"etudiant_id": "S123", "nom": "Test", "prenom": "User"}
        r = await client.post("/", json=payload)
        assert r.status_code == status.HTTP_201_CREATED
        assert r.json()["etudiant_id"] == "S123"

        r2 = await client.get("/search?nom=Test")
        assert r2.status_code == 200
        assert any(s["nom"] == "Test" for s in r2.json())
