import pytest
from httpx import AsyncClient
from fastapi import status

@pytest.mark.asyncio
async def test_health(client: AsyncClient):
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

@pytest.mark.asyncio
async def test_security_headers(client: AsyncClient):
    response = await client.get("/health")
    assert "X-Frame-Options" in response.headers
    assert response.headers["X-Frame-Options"] == "DENY"
    assert "Content-Security-Policy" in response.headers
    assert "Strict-Transport-Security" in response.headers

@pytest.mark.asyncio
async def test_public_paths_no_auth(client: AsyncClient):
    # Discovery is a public path
    response = await client.get("/discovery")
    # It will try to connect to other services and fail in test environment,
    # but it shouldn't be 401.
    assert response.status_code != 401

@pytest.mark.asyncio
async def test_private_paths_need_auth(client: AsyncClient):
    # Accessing a service that is not in public paths
    response = await client.get("/api/institutions/")
    assert response.status_code == 401
