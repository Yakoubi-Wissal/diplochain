import os
import subprocess
import pytest
from httpx import AsyncClient
from main import app

# indicate to the application that we're running in a test context
os.environ["TESTING"] = "1"

# use pytest-asyncio for asynchronous tests
pytestmark = pytest.mark.asyncio

@pytest.fixture(scope="session", autouse=True)
def init_database():
    """Reset and seed the database before any tests run.

    Executed once per pytest session; required when running against multiple
    anyio backends so each gets a fresh schema.
    """

    subprocess.run([
        "./venv/bin/python", "init_db.py",
        "--reset", "--seed-admin", "superadmin@diplochain.com", "superadmin123"
    ], check=True)
    yield



async def test_health(async_client):
    r = await async_client.get("/")
    assert r.status_code == 200


async def test_docs(async_client):
    r = await async_client.get("/docs")
    assert r.status_code == 200


async def test_404(async_client):
    r = await async_client.get("/nonexistent")
    assert r.status_code == 404



async def test_dashboard_protected(async_client):
    # endpoints requiring authentication/roles should return 401 when unauthenticated
    for path in ["/admin/metrics", "/admin/students", "/admin/institutions"]:
        r = await async_client.get(path)
        assert r.status_code in (401, 403)  # depending on auth implementation


async def test_dashboard_authenticated(async_client):
    # login first to get token
    r = await async_client.post(
        "/auth/login",
        data={"username": "superadmin@diplochain.com", "password": "superadmin123"},
    )
    assert r.status_code == 200
    token = r.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # metrics returns list (possibly empty)
    r = await async_client.get("/admin/metrics", headers=headers)
    assert r.status_code == 200
    assert isinstance(r.json(), list)

    # student and institution views should also be accessible and return lists
    for path in ["/admin/students", "/admin/institutions"]:
        r = await async_client.get(path, headers=headers)
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    # metrics refresh should succeed
    r = await async_client.post("/admin/metrics/refresh", headers=headers)
    assert r.status_code == 200
    assert r.json().get("status") == "ok"

    # create a new institution (note trailing slash to avoid 307 redirect)
    r = await async_client.post("/institutions/", headers=headers, params={"nom_institution":"Inst2","code":"C2"})
    # if a redirect still occurs we follow it manually; expect final result 201
    if r.status_code == 307:
        # follow the redirect location
        location = r.headers.get("location")
        assert location, "redirect without location header"
        r = await async_client.post(location, headers=headers, params={"nom_institution":"Inst2","code":"C2"})
    assert r.status_code == 201
    inst = r.json()
    assert inst["nom_institution"] == "Inst2"
    inst_id = inst["institution_id"]
    r = await async_client.patch(f"/institutions/{inst_id}", headers=headers, params={"nom_institution":"Inst2b","status":"SUSPENDED"})
    assert r.status_code == 200
    assert r.json()["nom_institution"] == "Inst2b"


async def test_update_user_email(async_client):
    # make sure superadmin email is correct before attempting login; previous tests
    # may have mutated it during earlier runs.
    from database import AsyncSessionLocal
    from sqlalchemy import text
    async with AsyncSessionLocal() as db:
        await db.execute(text("UPDATE \"User\" SET email='superadmin@diplochain.com' WHERE id_user=1"))
        await db.commit()

    # login manually (avoids relying on auth_headers fixture which once failed)
    r = await async_client.post(
        "/auth/login",
        data={"username": "superadmin@diplochain.com", "password": "superadmin123"},
    )
    assert r.status_code == 200, f"login failed in update test: {r.status_code} {r.text}"
    token = r.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # change superadmin email temporarily
    r = await async_client.patch("/users/1", json={"email": "changed@diplochain.com"}, headers=headers)
    assert r.status_code == 200, r.text
    assert r.json()["email"] == "changed@diplochain.com"

    # revert back to original address so later fixtures still work
    r = await async_client.patch("/users/1", json={"email": "superadmin@diplochain.com"}, headers=headers)
    assert r.status_code == 200, r.text
    assert r.json()["email"] == "superadmin@diplochain.com"


# a reusable fixture to obtain valid auth headers by logging in once
@pytest.fixture
async def auth_headers(async_client):
    r = await async_client.post(
        "/auth/login",
        data={"username": "superadmin@diplochain.com", "password": "superadmin123"},
    )
    assert r.status_code == 200, f"login failed during fixture: {r.status_code} {r.text}"
    return {"Authorization": f"Bearer {r.json()["access_token"]}"}


async def test_metrics_counts_confirmed(async_client, auth_headers):
    # create one diploma then manually mark it CONFIRME, refresh metrics and expect count ≥1
    # headers come from fixture
    headers = auth_headers

    # emit a diploma (status will be ORIGINAL by service)
    # use uuid to guarantee unique digest every run
    import uuid
    pdf_content = uuid.uuid4().hex.encode()
    files = {"pdf_file": ("dummy.pdf", pdf_content, "application/pdf")}
    data = {
        "titre": "Confirm Test",
        "etudiant_id": "E001",
        "institution_id": 1,
    }
    r = await async_client.post("/diplomes/emit/upload", files=files, data=data, headers=headers)
    assert r.status_code == 201, r.text
    dipl_id = r.json()["id_diplome"]

    # manually set CONFIRME via direct DB access
    from database import AsyncSessionLocal
    from sqlalchemy import text
    async with AsyncSessionLocal() as db:
        await db.execute(text("UPDATE diplome_blockchain_ext SET statut='CONFIRME' WHERE id_diplome=:id"), {"id": dipl_id})
        await db.commit()

    # refresh metrics and check confirm count
    r = await async_client.post("/admin/metrics/refresh", headers=headers)
    assert r.status_code == 200
    r = await async_client.get("/admin/metrics", headers=headers)
    assert r.status_code == 200
    row = r.json()[0]
    assert row.get("nb_diplomes_confirmes", 0) >= 1


async def test_login_superadmin(async_client):
    # login using seeded credentials
    r = await async_client.post(
        "/auth/login",
        data={"username": "superadmin@diplochain.com", "password": "superadmin123"},
    )
    assert r.status_code == 200, r.text
    data = r.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


async def test_diplome_lifecycle(async_client):
    # create a dummy diploma via upload, update, revoke flow
    # login first
    r = await async_client.post(
        "/auth/login",
        data={"username": "superadmin@diplochain.com", "password": "superadmin123"},
    )
    token = r.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # prep a fake PDF
    pdf_content = b"%PDF-1.4 dummy"
    files = {"pdf_file": ("dummy.pdf", pdf_content, "application/pdf")}       
    data = {
        "titre": "Test Diploma",
        "etudiant_id": "E001",
        "institution_id": 1,
    }
    r = await async_client.post("/diplomes/emit/upload", files=files, data=data, headers=headers)
    assert r.status_code == 201, r.text
    dipl = r.json()
    assert dipl["titre"] == "Test Diploma"
    diplome_id = dipl["id_diplome"]

    # update diploma title
    r = await async_client.patch(f"/diplomes/{diplome_id}", json={"titre": "Updated"}, headers=headers)
    assert r.status_code == 200
    assert r.json()["titre"] == "Updated"

    # revoke the diploma
    r = await async_client.patch(f"/diplomes/{diplome_id}/revoquer", json={"commentaire":"erratum"}, headers=headers)
    assert r.status_code == 200
    assert r.json()["statut"] == "REVOQUE"
