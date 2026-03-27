import pytest
import hashlib
from unittest.mock import AsyncMock, MagicMock, patch
from httpx import AsyncClient, ASGITransport
from main import app

@pytest.mark.asyncio
async def test_health(client: AsyncClient):
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

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

    # We need to mock the httpx.AsyncClient that is used INSIDE the route
    with patch("httpx.AsyncClient") as MockClient:
        instance = MockClient.return_value
        instance.__aenter__.return_value = instance
        instance.get = AsyncMock(side_effect=[mock_bc_response, mock_ipfs_response])

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            r = await client.get("/verify/opaque_diploma_001")
            assert r.status_code == 200
            data = r.json()
            assert data["is_valid"] is True
            assert data["identifiant_opaque"] == "opaque_diploma_001"

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

    with patch("httpx.AsyncClient") as MockClient:
        instance = MockClient.return_value
        instance.__aenter__.return_value = instance
        instance.get = AsyncMock(side_effect=[mock_bc_response, mock_ipfs_response])

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            r = await client.get("/verify/opaque_tampered_001")
            assert r.status_code == 200
            data = r.json()
            assert data["is_valid"] is False
