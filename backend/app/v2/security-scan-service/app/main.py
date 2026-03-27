from fastapi import FastAPI
import asyncio
import logging
import httpx
from datetime import datetime

app = FastAPI(title="security-scan-service", version="1.0.0")
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("security-scan-service")

SERVICES = {
    "api-gateway": "http://api-gateway:8000",
    "user-service": "http://user-service:8000",
    "blockchain-service": "http://blockchain-service:8000",
    "analytics-service": "http://analytics-service:8000"
}

async def scan_owasp_top_10():
    findings = []
    async with httpx.AsyncClient() as client:
        for name, url in SERVICES.items():
            try:
                resp = await client.get(url, timeout=2.0)
                if 'X-Frame-Options' not in resp.headers:
                    findings.append({"service": name, "finding": "Missing X-Frame-Options"})
            except Exception as e:
                logger.error(f"Scan failed for {name}: {str(e)}")
    return findings

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.post("/scan/now")
async def trigger_scan():
    findings = await scan_owasp_top_10()
    return {"status": "completed", "findings": findings}

async def scan_loop():
    logger.info("Security Scan Service Started.")
    while True:
        try:
            await scan_owasp_top_10()
        except: pass
        await asyncio.sleep(300)

@app.on_event("startup")
async def startup():
    asyncio.create_task(scan_loop())

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
