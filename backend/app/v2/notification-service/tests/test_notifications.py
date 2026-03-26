import pytest
from fastapi import status

@pytest.mark.asyncio
async def test_notification_operations(client):
    payload = {
        "user_id": 99,
        "type_notification": "EMAIL",
        "message": "Welcome to DiploChain!"
    }
    # Router included at root, so use "/" instead of "/notifications/"
    r = await client.post("/", json=payload)
    # The router doesn't explicitly set 201, it returns 200 by default for POST
    assert r.status_code == status.HTTP_200_OK
    assert r.json()["message"] == "Welcome to DiploChain!"

    # Field is "id" not "id_notification" according to models.py
    assert "id" in r.json()

    r2 = await client.get(f"/user/99")
    assert r2.status_code == 200
    assert len(r2.json()) > 0
