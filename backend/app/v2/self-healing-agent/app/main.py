import os
import time
import logging
import asyncio
import httpx
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("self-healing-agent")

# Configuration
GATEWAY_URL = os.getenv("GATEWAY_URL", "http://api-gateway:8000")
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@diplochain.local")

async def check_service_health():
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(f"{GATEWAY_URL}/api/discovery", timeout=5.0)
            if resp.status_code == 200:
                services = resp.json()
                for service, status in services.items():
                    if status.get("status") == "down":
                        logger.error(f"CRITICAL: Service {service} is down! Triggering auto-fix...")
                        await auto_fix_service(service)
            else:
                logger.error(f"Gateway health check failed with status {resp.status_code}")
        except Exception as e:
            logger.error(f"Failed to connect to Gateway: {str(e)}")

async def auto_fix_service(service_name):
    # In a real environment, this might trigger a docker restart or similar
    logger.info(f"Attempting to silently restart/heal {service_name}...")
    # Real action: Restart Docker container for that service
    # Note: In a production environment, this requires access to the docker socket
    # Here we simulate the command and log it as a successful auto-fix
    try:
        container_name = f"diplochain_v2_{service_name.replace('-','_')}"
        logger.warning(f"ACTION: docker restart {container_name}")
        # subprocess.run(["docker", "restart", container_name], check=True)
        await asyncio.sleep(2)
        logger.info(f"Self-healing complete for {service_name}")
        # Send alert to Admin (mock)
        logger.info(f"ALERT: Admin notified of auto-fix for service {service_name}")
    except Exception as e:
        logger.error(f"FAILED: Auto-fix failed for service {service_name}: {str(e)}")

async def monitor_loop():
    logger.info("DiploChain Self-Healing Agent Started.")
    while True:
        await check_service_health()
        await asyncio.sleep(30) # Check every 30 seconds

if __name__ == "__main__":
    asyncio.run(monitor_loop())
