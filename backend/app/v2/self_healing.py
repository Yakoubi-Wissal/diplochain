import os
import time
import logging
import httpx
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Configuration
DB_URL = os.getenv("DATABASE_URL", "postgresql://diplochain_user:diplochain_pass@postgres/diplochain_db")
CHECK_INTERVAL = 30  # seconds

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("self-healing")

def check_db():
    try:
        engine = create_engine(DB_URL.replace("postgresql+asyncpg://", "postgresql://"))
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return False

def check_service(name, url):
    try:
        response = httpx.get(f"{url}/health", timeout=5.0)
        if response.status_code == 200:
            return True
        else:
            logger.warning(f"Service {name} returned status {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"Service {name} health check failed: {e}")
        return False

SERVICES = {
    "api-gateway": "http://api-gateway:8000",
    "user-service": "http://user-service:8000",
}

def heal():
    logger.info("Starting self-healing monitor...")
    while True:
        if not check_db():
            logger.critical("DATABASE DOWN - Manual intervention might be required if it doesn't auto-restart")

        for name, url in SERVICES.items():
            if not check_service(name, url):
                logger.error(f"SERVICE {name} DOWN - Attempting to log anomaly")
                # In a real docker environment, we might try to restart the container via docker API
                # For now, we simulate by logging the event for the admin

        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    heal()
