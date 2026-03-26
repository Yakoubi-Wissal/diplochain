import pytest
from fastapi import status

@pytest.mark.asyncio
async def test_dashboard_metrics(client):
    # Testing GET /metrics
    r = await client.get("/metrics")
    assert r.status_code == status.HTTP_200_OK
    assert isinstance(r.json(), list)

    # Testing health
    r2 = await client.get("/health")
    assert r2.status_code == 200
    assert r2.json() == {"status": "healthy"}
