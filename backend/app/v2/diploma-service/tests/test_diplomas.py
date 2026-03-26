import pytest
from fastapi import status

@pytest.mark.asyncio
async def test_diploma_crud(client):
    payload = {
        "titre": "D1",
        "mention": "A",
        "date_emission": "2025-01-01",
        "hash_sha256": "h" * 64,
        "ipfs_cid": "cid123",
        "etudiant_id": "E1",
        "institution_id": 1,
        "uploaded_by": 1,
        "session_diplome": "P",
        "id_annexe": 1,
        "num_diplome": 123
    }
    # Router included at root, so use "/" instead of "/diplomas/"
    r = await client.post("/", json=payload)
    assert r.status_code == status.HTTP_200_OK
    data = r.json()
    assert data["titre"] == "D1"
    did = data["id_diplome"]

    r2 = await client.get(f"/{did}")
    assert r2.status_code == status.HTTP_200_OK
    assert r2.json()["id_diplome"] == did

    r3 = await client.post(f"/{did}/revoke")
    assert r3.status_code == status.HTTP_200_OK
    assert r3.json()["statut"] == "REVOQUE"
