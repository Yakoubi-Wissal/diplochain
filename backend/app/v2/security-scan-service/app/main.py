import os
import json
import logging
import asyncio
import httpx
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("security-scan-service")

# Configuration
SERVICES = {
    "api-gateway": "http://api-gateway:8000",
    "user-service": "http://user-service:8000",
    "blockchain-service": "http://blockchain-service:8000",
    "analytics-service": "http://analytics-service:8000"
}

async def scan_owasp_top_10():
    # Simulate scanning for common vulnerabilities like SQL Injection, Broken Auth, etc.
    # In a real system, we might use tools like OWASP ZAP or Bandit here
    findings = []

    async with httpx.AsyncClient() as client:
        for name, url in SERVICES.items():
            try:
                # 1. Check for insecure headers
                resp = await client.get(url, timeout=2.0)
                if 'X-Frame-Options' not in resp.headers:
                    findings.append({"service": name, "finding": "Missing X-Frame-Options (Clickjacking)"})
                if 'Content-Security-Policy' not in resp.headers:
                    findings.append({"service": name, "finding": "Missing CSP Header (XSS)"})

                # 2. Check for exposed metrics/admin endpoints
                admin_check = await client.get(f"{url}/admin", timeout=1.0)
                if admin_check.status_code == 200:
                    findings.append({"service": name, "finding": "Admin endpoint exposed without auth"})
            except Exception as e:
                logger.error(f"Scan failed for {name}: {str(e)}")

    return findings

async def scan_loop():
    logger.info("Security Scan Service Started.")
    while True:
        findings = await scan_owasp_top_10()
        if findings:
            logger.warning(f"SECURITY ALERT: {len(findings)} findings detected!")
            for f in findings:
                logger.warning(f" - {f['service']}: {f['finding']}")

        # In a real environment, post results to analytics-service
        try:
           async with httpx.AsyncClient() as client:
               await client.post("http://analytics-service:8000/security/scan", json={"findings": findings})
        except: pass

        await asyncio.sleep(60 * 5) # Scan every 5 minutes

if __name__ == "__main__":
    asyncio.run(scan_loop())
