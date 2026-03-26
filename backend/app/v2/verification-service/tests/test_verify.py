import pytest
from fastapi import status

@pytest.mark.asyncio
async def test_qr_and_history(client):
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
        "timestamp": "2023-01-01T00:00:00",
        "ancien_hash": None,
        "ip_address": None,
        "ms_tenant_id": None,
        "commentaire": None,
        "user_agent": None
    }
    r2 = await client.post("/history", json=hist)
    if r2.status_code == 422:
        print(f"422 Detail: {r2.json()}")
    assert r2.status_code == status.HTTP_200_OK
    assert "historique_operations_id" in r2.json()
