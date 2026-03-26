from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.config import settings
from core.database import engine, Base
import core.models

from routers import analytics

@asynccontextmanager
async def lifespan(app: FastAPI):
    if not str(engine.url).endswith(":memory:"):
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    yield

app = FastAPI(title="analytics-service", version="1.0.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

@app.get("/")
async def root():
    return {"service": "analytics-service", "status": "running"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

app.include_router(analytics.router, prefix="")
