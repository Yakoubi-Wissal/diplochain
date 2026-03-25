from fastapi import FastAPI, Request, HTTPException, Response
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import httpx
import jwt
import os
import time
import json
import logging
from typing import Optional

# Setup logging for anomalies
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("api-gateway")

app = FastAPI(
    title="DiploChain API Gateway",
    version="1.0.0",
    description="Routes frontend requests to microservices",
)

# CORS: Restrict to known origins (e.g., localhost:3000 for React)
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:3001,http://localhost:8000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")

PUBLIC_PATHS = [
    "/api/users/auth/login",
    "/api/user-service/auth/login",
    "/api/users/", # Permit registration
    "/api/user-service/",
    "/discovery",
    "/health",
    "/api/health",
    "health" # Catch all for any path containing /health
]

def verify_token(token: str) -> bool:
    try:
        jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return True
    except Exception:
        return False

SERVICE_MAP = {
    "users": "http://user-service:8000",
    "user-service": "http://user-service:8000",
    "institutions": "http://institution-service:8000",
    "institution-service": "http://institution-service:8000",
    "students": "http://student-service:8000",
    "student-service": "http://student-service:8000",
    "diplomas": "http://diploma-service:8000",
    "diploma-service": "http://diploma-service:8000",
    "documents": "http://document-service:8000",
    "document-service": "http://document-service:8000",
    "blockchain": "http://blockchain-service:8000",
    "blockchain-service": "http://blockchain-service:8000",
    "storage": "http://storage-service:8000",
    "storage-service": "http://storage-service:8000",
    "verify": "http://verification-service:8000",
    "verification-service": "http://verification-service:8000",
    "analytics": "http://analytics-service:8000",
    "analytics-service": "http://analytics-service:8000",
    "entreprises": "http://entreprise-service:8000",
    "entreprise-service": "http://entreprise-service:8000",
    "notifications": "http://notification-service:8000",
    "notification-service": "http://notification-service:8000",
    "pdf": "http://pdf-generator-service:8000",
    "pdf-generator-service": "http://pdf-generator-service:8000",
    "admin": "http://admin-dashboard-service:8000",
    "admin-dashboard-service": "http://admin-dashboard-service:8000",
    "qr": "http://qr-validation-service:8000",
    "qr-validation-service": "http://qr-validation-service:8000",
}

@app.middleware("http")
async def monitor_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time

    # Simple anomaly detection: log if request takes too long
    if process_time > 2.0:
        logger.warning(f"ANOMALY: Slow request to {request.url.path} took {process_time:.2f}s")

    # Log errors
    if response.status_code >= 400:
        logger.error(f"ANOMALY: Request to {request.url.path} failed with status {response.status_code}")

    return response

@app.api_route("/api/{service}/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy(service: str, path: str, request: Request):
    # 1. Check if path is public
    full_path = f"/api/{service}/{path}"
    match_path = full_path.rstrip("/")
    is_public = any(match_path.startswith(p.rstrip("/")) for p in PUBLIC_PATHS)
    
    if not is_public:
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Missing or invalid token")
        
        token = auth_header.split(" ")[1]
        if not verify_token(token):
            raise HTTPException(status_code=401, detail="Invalid token")

    base = SERVICE_MAP.get(service)
    if not base:
        return {"error": "unknown service"}

    url_path = path if not path.startswith("/") else path[1:]
    url = f"{base}/{url_path}"
    
    async with httpx.AsyncClient() as client:
        resp = await client.request(
            request.method,
            url,
            headers={k: v for k, v in request.headers.items() if k.lower() != "host"},
            content=await request.body(),
            params=request.query_params,
        )
        
        content_type = resp.headers.get("content-type", "")
        headers = {k: v for k, v in resp.headers.items() if k.lower() not in ["content-length", "content-encoding"]}
        
        if "application/json" in content_type:
            try:
                json_content = resp.json()
                return JSONResponse(
                    content=json_content,
                    status_code=resp.status_code,
                    headers=headers
                )
            except Exception:
                pass
        
        return Response(
            content=resp.content,
            status_code=resp.status_code,
            headers=headers
        )

@app.get("/discovery")
@app.get("/api/discovery")
async def discovery():
    import asyncio
    async def get_service_status(client, service, url):
        try:
            r = await client.get(f"{url}/health", timeout=1.0)
            return service, {"status": "up", "health": r.json() if r.status_code == 200 else r.status_code}
        except Exception as e:
            return service, {"status": "down", "error": str(e)}

    results = {}
    async with httpx.AsyncClient() as client:
        tasks = [get_service_status(client, s, u) for s, u in SERVICE_MAP.items()]
        completed = await asyncio.gather(*tasks)
        for service, status in completed:
            results[service] = status
    return results

@app.get("/health")
async def health():
    return {"status": "ok"}
