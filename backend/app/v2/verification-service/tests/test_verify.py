import sys, pathlib
service_root = pathlib.Path(__file__).parent.parent
app_pkg = service_root / "app"
if str(app_pkg) not in sys.path:
    sys.path.insert(0, str(app_pkg))

import pytest
from httpx import AsyncClient, ASGITransport
from fastapi import status

from main import app

@pytest.mark.asyncio
async def test_qr_and_history():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        qr = {"diplome_id": 1, "etudiant_id": "E1", "qr_code_path": "p.png", "identifiant_opaque": "abc", "url_verification": "http://x"}
        r = await client.post("/qr", json=qr)
        assert r.status_code == status.HTTP_200_OK
        assert "qr_code_records_id" in r.json()

        hist = {
            "diplome_id": 1,
            "type_operation": "VERIFICATION",
            "nouvel_hash": "h",
            "tx_id_fabric": "t",
            "acteur_id": 1,
            "historique_operations_id": 0,
            "ancien_hash": None,
            "timestamp": "2023-01-01T00:00:00"
        }
        r2 = await client.post("/history", json=hist)
        if r2.status_code != 200:
            print(r2.json())
        assert r2.status_code == status.HTTP_200_OK
        assert "historique_operations_id" in r2.json()
