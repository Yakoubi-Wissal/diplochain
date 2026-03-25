from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.config import settings
from core.database import engine, Base

from routers import users, auth, roles

app = FastAPI(
    title="user-service",
    description="DiploChain User Service",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.get("/")
async def root():
    return {"service": "user-service", "status": "running"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

# Seed endpoint removed


app.include_router(users.router, prefix="/users")
app.include_router(auth.router, prefix="/auth")
app.include_router(roles.router, prefix="/roles")
