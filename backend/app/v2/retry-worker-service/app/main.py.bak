from fastapi import FastAPI
app = FastAPI()

import asyncio
import logging
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    BLOCKCHAIN_URL: str = "http://blockchain-service:8000"

    class Config:
        env_file = ".env"

settings = Settings()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("retry-worker")

engine = create_async_engine(settings.DATABASE_URL, future=True)

async def check_pending_diplomas():
    logger.info("Running retry job...")
    async with engine.begin() as conn:
        # Step 1: Query pending diplomas
        query = text("""
            SELECT diplome_id, hash_sha256, ipfs_cid, blockchain_retry_count 
            FROM diplomes 
            WHERE statut = 'PENDING_BLOCKCHAIN' 
            AND blockchain_retry_count < 5
        """)
        result = await conn.execute(query)
        rows = result.fetchall()

        for row in rows:
            diplome_id = row.diplome_id
            hash_sha256 = row.hash_sha256
            ipfs_cid = row.ipfs_cid
            retry_count = row.blockchain_retry_count

            logger.info(f"Retrying diploma {diplome_id} (Attempt {retry_count + 1})")
            
            # Simulated logic to call fabric via blockchain-service:
            # async with httpx.AsyncClient() as client:
            #     resp = await client.post(...)
            
            # If failed:
            await conn.execute(
                text("UPDATE diplomes SET blockchain_retry_count = blockchain_retry_count + 1 WHERE diplome_id = :id"),
                {"id": diplome_id}
            )

async def main():
    logger.info("Starting Retry Worker Service...")
    while True:
        try:
            await check_pending_diplomas()
        except Exception as e:
            logger.error(f"Error checking pending diplomas: {e}")
        
        # Sleep for 1 minute before next run
        await asyncio.sleep(60)

if __name__ == "__main__":
    asyncio.run(main())
