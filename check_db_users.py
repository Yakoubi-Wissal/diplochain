import asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import sys

# Update these to match your environment if needed
DATABASE_URL = "postgresql+asyncpg://diplochain_user:diplochain_pass@localhost:5432/diplochain_db"

async def check_user():
    engine = create_async_engine(DATABASE_URL)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        try:
            from core.models import User # Assuming this works if run from common root
        except:
            # Manual query if model import fails
            from sqlalchemy import text
            result = await session.execute(text('SELECT id_user, email, status FROM "User"'))
            rows = result.all()
            print(f"Users found: {len(rows)}")
            for row in rows:
                print(row)
            return
            
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(check_user())
