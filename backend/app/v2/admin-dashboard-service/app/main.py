from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.config import settings
from core.database import engine, Base
import core.models

from routers import dashboard

app = FastAPI(title="admin-dashboard-service", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.get("/")
async def root():
    return {"service": "admin-dashboard-service", "status": "running"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

app.include_router(dashboard.router, prefix="")
