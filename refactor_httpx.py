import os, glob

for fname in glob.glob('/home/wissal/diplochain/backend/app/v2/*/tests/*.py'):
    with open(fname, 'r') as f:
        content = f.read()
    
    if 'AsyncClient(app=app' in content:
        if 'ASGITransport' not in content:
            content = content.replace('from httpx import AsyncClient', 'from httpx import AsyncClient, ASGITransport')
        content = content.replace('AsyncClient(app=app', 'AsyncClient(transport=ASGITransport(app=app)')
        with open(fname, 'w') as f:
            f.write(content)
        print(f'Fixed {fname}')
