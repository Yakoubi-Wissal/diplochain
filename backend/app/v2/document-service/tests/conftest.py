import sys
import pathlib

# Put both service root and its ``app`` package on sys.path so imports from
# ``app`` can reach sibling packages like ``routers`` or ``core``.
service_root = pathlib.Path(__file__).parent.parent
app_pkg = service_root / "app"
for p in (service_root, app_pkg):
    sp = str(p)
    if sp not in sys.path:
        sys.path.insert(0, sp)

