import pytest
from httpx import AsyncClient
from fastapi import status

@pytest.mark.asyncio
async def test_qr_and_history(client: AsyncClient):
    # Test Create QR
    qr_payload = {
        "diplome_id": 1,
        "etudiant_id": "E1",
        "qr_code_path": "path/to/qr.png",
        "identifiant_opaque": "opaque123",
        "url_verification": "http://verify.it/opaque123"
    }
    response = await client.post("/qr", json=qr_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["identifiant_opaque"] == "opaque123"

    # Test Read QR
    qr_id = data["qr_code_records_id"]
    response = await client.get(f"/qr/{qr_id}")
    assert response.status_code == 200
    assert response.json()["identifiant_opaque"] == "opaque123"
