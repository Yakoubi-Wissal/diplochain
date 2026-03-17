import sys, pathlib
# adjust path so this service's root and its app package are first
service_root = pathlib.Path(__file__).parent.parent
app_folder = service_root / "app"
for p in (service_root, app_folder):
    sp = str(p)
    if sp not in sys.path:
        sys.path.insert(0, sp)
# remove conflicting modules from earlier services
for name in list(sys.modules):
    if name == "routers" or name.startswith("routers.") or name == "core" or name.startswith("core."):
        del sys.modules[name]

import pytest
import httpx

BASE_URL = "http://localhost:8000"

@pytest.mark.asyncio
async def test_rapport_operations():
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.get(f"{BASE_URL}/rapports/")
        assert r.status_code == 200
