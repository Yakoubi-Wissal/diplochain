from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import httpx

app = FastAPI(
    title="DiploChain API Gateway",
    version="1.0.0",
    description="Routes frontend requests to microservices",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

@app.api_route("/api/{service}/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy(service: str, path: str, request: Request):
    base = SERVICE_MAP.get(service)
    if not base:
        return {"error": "unknown service"}

    # Ensure we don't end up with double slashes but preserve the trailing slash intent
    url_path = path if not path.startswith("/") else path[1:]
    
    # Standard proxy: /api/service/path -> base/service/path
    # This aligns with microservices having prefixes like /users, /auth, etc.
    url = f"{base}/{url_path}"
    
    async with httpx.AsyncClient() as client:
        print(f"DEBUG: Proxying {request.method} {request.url} -> {url}")
        resp = await client.request(
            request.method,
            url,
            headers={k: v for k, v in request.headers.items() if k.lower() != "host"},
            content=await request.body(),
            params=request.query_params,
        )
        
        # Determine how to return the response based on Content-Type
        content_type = resp.headers.get("content-type", "")
        headers = {k: v for k, v in resp.headers.items() if k.lower() not in ["content-length", "content-encoding"]}
        
        if resp.status_code >= 400:
            print(f"DEBUG: Backend error {resp.status_code}: {resp.text}")
        
        print(f"DEBUG: Backend returned {resp.status_code}")
        
        if "application/json" in content_type:
            from fastapi.responses import JSONResponse
            try:
                json_content = resp.json()
                return JSONResponse(
                    content=json_content,
                    status_code=resp.status_code,
                    headers=headers
                )
            except Exception:
                # Fallback to plain response if json parsing fails
                pass
        
        from fastapi import Response
        return Response(
            content=resp.content,
            status_code=resp.status_code,
            headers=headers
        )

@app.get("/discovery")
async def discovery():
    """Probes all microservices and returns their status"""
    status = {}
    async with httpx.AsyncClient(timeout=2) as client:
        for service, url in SERVICE_MAP.items():
            try:
                # Try health endpoint first
                r = await client.get(f"{url}/health")
                if r.status_code == 200:
                    status[service] = {"status": "up", "health": r.json()}
                else:
                    status[service] = {"status": "reachable", "code": r.status_code}
            except Exception as e:
                status[service] = {"status": "down", "error": str(e)}
    return status

@app.get("/health")
async def health():
    return {"status": "ok"}
