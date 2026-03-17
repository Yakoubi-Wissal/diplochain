import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

import pytest
from httpx import AsyncClient
from fastapi import status

from app.main import app

@pytest.mark.asyncio
async def test_qr_and_history():
    async with AsyncClient(app=app, base_url="http://test") as client:
        qr = {"diplome_id": 1, "etudiant_id": "E1", "qr_code_path": "p.png", "identifiant_opaque": "abc", "url_verification": "http://x"}
        r = await client.post("/verify/qr", json=qr)
        assert r.status_code == status.HTTP_200_OK
        assert "qr_code_records_id" in r.json()

        hist = {"diplome_id":1, "type_operation":"VERIFICATION", "nouvel_hash":"h","tx_id_fabric":"t","acteur_id":1}
        r2 = await client.post("/verify/history", json=hist)
        assert r2.status_code == status.HTTP_200_OK
        assert "historique_operations_id" in r2.json()
