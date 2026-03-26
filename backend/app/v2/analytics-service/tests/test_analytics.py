import pytest
from httpx import AsyncClient
from fastapi import status
from app.core.models import StabilityHistory
from sqlalchemy import select

@pytest.mark.asyncio
async def test_health_and_metrics(client: AsyncClient, db_session):
    r = await client.get("/health")
    assert r.status_code == status.HTTP_200_OK

    r2 = await client.get("/metrics/daily")
    assert r2.status_code == status.HTTP_200_OK

@pytest.mark.asyncio
async def test_audit_events(client: AsyncClient, db_session):
    # Create an event
    event_data = {
        "service": "test-service",
        "event_type": "TEST_EVENT",
        "details": "This is a test event",
        "severity": "INFO"
    }
    r = await client.post("/events", json=event_data)
    assert r.status_code == status.HTTP_200_OK
    data = r.json()
    assert data["service"] == "test-service"
    assert "id" in data

    # List events
    r = await client.get("/events")
    assert r.status_code == status.HTTP_200_OK
    events = r.json()
    assert len(events) >= 1
    assert events[0]["event_type"] == "TEST_EVENT"

@pytest.mark.asyncio
async def test_security_scan_and_stability(client: AsyncClient, db_session):
    # Initial stability
    r = await client.get("/metrics/stability")
    assert r.status_code in [200, 201]

    # Post a scan
    scan_data = {
        "findings": [
            {"service": "api-gateway", "finding": "Missing X-Frame-Options"},
            {"service": "user-service", "finding": "Missing CSP Header"}
        ]
    }
    r = await client.post("/security/scan", json=scan_data)
    assert r.status_code in [200, 201]
    assert r.json()["security_score"] == 80 # 100 - 2*10

    # Check updated metrics
    r = await client.get("/metrics/stability")
    assert r.status_code in [200, 201]
    data = r.json()
    assert data["security"] == 80
