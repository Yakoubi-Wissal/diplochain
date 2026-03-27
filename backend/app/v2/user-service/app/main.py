from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.database import engine, Base
from core import models
from routers import auth, users, roles

app = FastAPI(title="user-service", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.get("/health")
async def health():
    return {"status": "healthy"}

app.include_router(auth.router, prefix="/auth")
app.include_router(roles.router, prefix="/roles")
app.include_router(users.router, prefix="")
