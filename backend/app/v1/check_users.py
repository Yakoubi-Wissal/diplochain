import asyncio
from database import AsyncSessionLocal
from sqlalchemy import text

async def check():
    async with AsyncSessionLocal() as db:
        r = await db.execute(text('SELECT id_user,email,password FROM "User"'))
        rows = r.fetchall()
        print('users', rows)

asyncio.run(check())
