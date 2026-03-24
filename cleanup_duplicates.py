import asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import bcrypt

DATABASE_URL = "postgresql+asyncpg://diplochain_user:diplochain_pass@localhost:5432/diplochain_db"

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

async def cleanup_db():
    engine = create_async_engine(DATABASE_URL)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    password_hash = hash_password("Admin@1234")
    
    async with async_session() as session:
        async with session.begin():
            # 1. Delete all users with this email
            await session.execute(
                text('DELETE FROM "UserRole" WHERE user_id IN (SELECT id_user FROM "User" WHERE email = :email)'),
                {"email": "admin@diplochain.tn"}
            )
            await session.execute(
                text('DELETE FROM "User" WHERE email = :email'),
                {"email": "admin@diplochain.tn"}
            )
            
            # 2. Insert fresh admin
            await session.execute(
                text('''
                    INSERT INTO "User" (username, email, password, status, revoked, expired)
                    VALUES (:username, :email, :password, :status, :revoked, :expired)
                '''),
                {
                    "username": "admin",
                    "email": "admin@diplochain.tn",
                    "password": password_hash,
                    "status": "ACTIVE",
                    "revoked": False,
                    "expired": False
                }
            )
            print("Successfully cleaned up duplicates and created fresh admin user.")
            
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(cleanup_db())
