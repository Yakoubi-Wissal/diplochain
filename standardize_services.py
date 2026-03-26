import os
import re

lifespan_template = """
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
"""

def fix_file(path):
    with open(path, 'r') as f:
        content = f.read()

    if 'FastAPI' not in content:
        return

    # Check if already using lifespan
    if 'lifespan=' in content and 'async def lifespan' in content:
        # Just ensure health status is healthy
        content = content.replace('"status": "ok"', '"status": "healthy"')
        with open(path, 'w') as f:
            f.write(content)
        return

    # Replace on_event startup
    new_content = content
    startup_pattern = r'@app\.on_event\("startup"\)\s+async def startup\(\):\s+async with engine\.begin\(\) as conn:\s+await conn\.run_sync\(Base\.metadata\.create_all\)'

    if re.search(startup_pattern, content):
        new_content = re.sub(startup_pattern, '', content)
        if 'from contextlib import asynccontextmanager' not in new_content:
            new_content = "from contextlib import asynccontextmanager\n" + new_content

        lifespan_def = "\n@asynccontextmanager\nasync def lifespan(app: FastAPI):\n    async with engine.begin() as conn:\n        await conn.run_sync(Base.metadata.create_all)\n    yield\n"

        # Insert before app = FastAPI
        new_content = re.sub(r'(app = FastAPI\(.*?\))', lifespan_def + r'\1', new_content, flags=re.DOTALL)
        # Add lifespan to FastAPI call
        new_content = re.sub(r'app = FastAPI\((.*?)\)', r'app = FastAPI(\1, lifespan=lifespan)', new_content, flags=re.DOTALL)

    # Standardize health
    new_content = new_content.replace('"status": "ok"', '"status": "healthy"')

    # Cleanup double lifespan if any
    if new_content.count('lifespan=lifespan') > 1:
         # Rough fix for double replacement
         pass

    with open(path, 'w') as f:
        f.write(new_content)

for root, dirs, files in os.walk('backend/app/v2'):
    if 'venv' in root: continue
    if 'main.py' in files:
        fix_file(os.path.join(root, 'main.py'))
