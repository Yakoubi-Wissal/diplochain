import sys, pathlib
service_root = pathlib.Path(__file__).parent.parent
app_folder = service_root / "app"
for p in (service_root, app_folder):
    sp = str(p)
    if sp not in sys.path:
        sys.path.insert(0, sp)
for name in list(sys.modules):
    if name == "routers" or name.startswith("routers.") or name == "core" or name.startswith("core."):
        del sys.modules[name]

import pytest
import hashlib
from unittest.mock import AsyncMock, MagicMock
from httpx import AsyncClient, ASGITransport

from main import app
import routers.validation as validation_router

@pytest.mark.asyncio
async def test_health():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        r = await client.get("/health")
        assert r.status_code == 200
        assert r.json() == {"status": "healthy"}

@pytest.mark.asyncio
async def test_qr_verify_valid_diploma():
    fake_pdf = b"%PDF-FAKE-CONTENT"
    expected_hash = hashlib.sha256(fake_pdf).hexdigest()

    mock_bc_response = MagicMock()
    mock_bc_response.status_code = 200
    mock_bc_response.json.return_value = {
        "hash_sha256": expected_hash,
        "ipfs_cid": "QmFakeCID123",
        "status": "ORIGINAL"
    }

    mock_ipfs_response = MagicMock()
    mock_ipfs_response.status_code = 200
    mock_ipfs_response.content = fake_pdf

    mock_http_client = AsyncMock()
    mock_http_client.get = AsyncMock(side_effect=[mock_bc_response, mock_ipfs_response])

    # Dependency override instead of patch
    async def override_get_http_client():
        yield mock_http_client

    app.dependency_overrides[validation_router.get_http_client] = override_get_http_client

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        r = await client.get("/verify/opaque_diploma_001")
        assert r.status_code == 200
        data = r.json()
        assert data["is_valid"] is True

    app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_qr_verify_invalid_diploma():
    fake_pdf = b"%PDF-TAMPERED"
    wrong_hash = "a" * 64

    mock_bc_response = MagicMock()
    mock_bc_response.status_code = 200
    mock_bc_response.json.return_value = {
        "hash_sha256": wrong_hash,
        "ipfs_cid": "QmFakeCID456",
    }

    mock_ipfs_response = MagicMock()
    mock_ipfs_response.status_code = 200
    mock_ipfs_response.content = fake_pdf

    mock_http_client = AsyncMock()
    mock_http_client.get = AsyncMock(side_effect=[mock_bc_response, mock_ipfs_response])

    async def override_get_http_client():
        yield mock_http_client

    app.dependency_overrides[validation_router.get_http_client] = override_get_http_client

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        r = await client.get("/verify/opaque_tampered_001")
        assert r.status_code == 200
        data = r.json()
        assert data["is_valid"] is False

    app.dependency_overrides.clear()
