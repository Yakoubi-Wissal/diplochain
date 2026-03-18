from fastapi import FastAPI
import asyncio
import logging
import httpx
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from pydantic_settings import BaseSettings

app = FastAPI(title="DiploChain Retry Worker Service", version="1.0.0")

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://diplochain_user:diplochain_pass@postgres/diplochain_db"
    BLOCKCHAIN_URL: str = "http://blockchain-service:8000"

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("retry-worker")

engine = create_async_engine(settings.DATABASE_URL, future=True)

# Track worker status for monitoring endpoint
worker_status = {
    "running": False,
    "last_run": None,
    "total_processed": 0,
    "total_failed": 0,
}


async def check_pending_diplomas():
    """Retries diplomas in PENDING_BLOCKCHAIN state via the blockchain-service.
    
    The blockchain metadata lives in diplome_blockchain_ext table (FK: id_diplome).
    Per init.sql (backend/database/init.sql line 94), the default statut is
    'PENDING_BLOCKCHAIN' — this is the value we query for.
    """
    logger.info("Running retry job...")
    async with engine.begin() as conn:
        # Real table: diplome_blockchain_ext, PK: id_diplome
        # Real enum default: 'PENDING_BLOCKCHAIN' (from init.sql line 94)
        # COALESCE handles NULL blockchain_retry_count (column has no DEFAULT in schema)
        query = text("""
            SELECT id_diplome, hash_sha256, ipfs_cid, statut,
                   COALESCE(blockchain_retry_count, 0) AS blockchain_retry_count
            FROM diplome_blockchain_ext
            WHERE statut = 'PENDING_BLOCKCHAIN'
            AND COALESCE(blockchain_retry_count, 0) < 5
        """)
        result = await conn.execute(query)
        rows = result.fetchall()

    for row in rows:
        diploma_id = row.id_diplome
        hash_sha256 = row.hash_sha256
        ipfs_cid = row.ipfs_cid
        retry_count = row.blockchain_retry_count

        logger.info(f"Retrying diploma {diploma_id} (Attempt {retry_count + 1})")

        success = False
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.post(
                    f"{settings.BLOCKCHAIN_URL}/blockchain/diplome",
                    json={
                        "id_diplome": diploma_id,
                        "hash_sha256": hash_sha256,
                        "ipfs_cid": ipfs_cid,
                        "statut": "CONFIRME",
                    }
                )
                if resp.status_code in (200, 201):
                    success = True
                    worker_status["total_processed"] += 1
                    logger.info(f"Diploma {diploma_id} confirmed on blockchain.")
        except Exception as e:
            logger.error(f"Failed to contact blockchain-service for diploma {diploma_id}: {e}")

        async with engine.begin() as conn:
            if success:
                await conn.execute(
                    text("UPDATE diplome_blockchain_ext SET statut = 'CONFIRME', blockchain_retry_count = blockchain_retry_count + 1 WHERE id_diplome = :id"),
                    {"id": diploma_id}
                )
            else:
                worker_status["total_failed"] += 1
                await conn.execute(
                    text("UPDATE diplome_blockchain_ext SET blockchain_retry_count = blockchain_retry_count + 1 WHERE id_diplome = :id"),
                    {"id": diploma_id}
                )


@app.get("/")
async def root():
    return {"service": "retry-worker-service", "status": "running"}


@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.get("/worker/status")
async def get_worker_status():
    """Monitor the current state of the retry worker."""
    return worker_status


@app.post("/worker/trigger")
async def trigger_worker():
    """Manually trigger the retry job."""
    try:
        await check_pending_diplomas()
        return {"triggered": True, "message": "Retry job executed successfully"}
    except Exception as e:
        return {"triggered": False, "error": str(e)}


async def worker_loop():
    """Infinite loop worker that runs every 60 seconds."""
    logger.info("Starting Retry Worker Service...")
    worker_status["running"] = True
    while True:
        from datetime import datetime
        worker_status["last_run"] = datetime.utcnow().isoformat()
        try:
            await check_pending_diplomas()
        except Exception as e:
            logger.error(f"Error checking pending diplomas: {e}")
        await asyncio.sleep(60)


@app.on_event("startup")
async def startup():
    asyncio.create_task(worker_loop())


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
