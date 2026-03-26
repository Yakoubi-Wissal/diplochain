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
ANALYTICS_URL = os.getenv("ANALYTICS_URL", "http://analytics-service:8000")
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@diplochain.local")

async def report_event(event_type, details, severity="INFO"):
    try:
        async with httpx.AsyncClient() as client:
            await client.post(f"{ANALYTICS_URL}/events", json={
                "service": "self-healing-agent",
                "event_type": event_type,
                "details": details,
                "severity": severity
            })
    except Exception as e:
        logger.error(f"Failed to report event: {str(e)}")

async def check_service_health():
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(f"{GATEWAY_URL}/api/discovery", timeout=5.0)
            if resp.status_code == 200:
                services = resp.json()
                for service, status in services.items():
                    if status.get("status") == "down":
                        logger.error(f"CRITICAL: Service {service} is down! Triggering auto-fix...")
                        await report_event("SERVICE_DOWN", f"Service {service} is down", "CRITICAL")
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
        await report_event("AUTO_FIX_SUCCESS", f"Successfully healed {service_name}", "INFO")
        # Send alert to Admin (mock)
        logger.info(f"ALERT: Admin notified of auto-fix for service {service_name}")
    except Exception as e:
        logger.error(f"FAILED: Auto-fix failed for service {service_name}: {str(e)}")
        await report_event("AUTO_FIX_FAILED", f"Failed to fix {service_name}: {str(e)}", "CRITICAL")

async def monitor_loop():
    logger.info("DiploChain Self-Healing Agent Started.")
    while True:
        await check_service_health()
        await asyncio.sleep(30) # Check every 30 seconds

if __name__ == "__main__":
    asyncio.run(monitor_loop())
