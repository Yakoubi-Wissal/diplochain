import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    r = client.get("/health")
    assert r.status_code in [200, 201]
    # some health endpoints return "ok", others "healthy"
    assert r.json()["status"] in ["ok", "healthy"]
