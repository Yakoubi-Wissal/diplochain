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
import httpx
from unittest.mock import AsyncMock, patch
from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest.mark.asyncio
async def test_health():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        r = await client.get("/health")
        assert r.status_code in [200, 201]
        assert r.json() == {"status": "healthy"}

@pytest.mark.asyncio
async def test_qr_verify_valid_diploma():
    """Test that a diploma with matching hashes is validated correctly."""
    fake_pdf = b"%PDF-FAKE-CONTENT"
    expected_hash = hashlib.sha256(fake_pdf).hexdigest()

    # Use real Response objects for better compatibility
    mock_bc_response = httpx.Response(200, json={
        "hash_sha256": expected_hash,
        "ipfs_cid": "QmFakeCID123",
        "status": "ORIGINAL"
    })
    mock_ipfs_response = httpx.Response(200, content=fake_pdf)

    mock_http_client = AsyncMock()
    # side_effect for an AsyncMock used as a method will return these on successive awaits
    mock_http_client.get.side_effect = [mock_bc_response, mock_ipfs_response]

    with patch("httpx.AsyncClient", return_value=mock_http_client):
        # We need to make sure the mock_http_client works as a context manager
        mock_http_client.__aenter__.return_value = mock_http_client

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            r = await client.get("/verify/opaque_diploma_001")
            assert r.status_code == 200
            data = r.json()
            assert data["is_valid"] is True
            assert data["identifiant_opaque"] == "opaque_diploma_001"

@pytest.mark.asyncio
async def test_qr_verify_invalid_diploma():
    """Test that tampered diploma is detected (hash mismatch)."""
    fake_pdf = b"%PDF-TAMPERED"
    wrong_hash = "a" * 64

    mock_bc_response = httpx.Response(200, json={
        "hash_sha256": wrong_hash,
        "ipfs_cid": "QmFakeCID456",
    })
    mock_ipfs_response = httpx.Response(200, content=fake_pdf)

    mock_http_client = AsyncMock()
    mock_http_client.get.side_effect = [mock_bc_response, mock_ipfs_response]
    mock_http_client.__aenter__.return_value = mock_http_client

    with patch("httpx.AsyncClient", return_value=mock_http_client):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            r = await client.get("/verify/opaque_tampered_001")
            assert r.status_code == 200
            data = r.json()
            assert data["is_valid"] is False
