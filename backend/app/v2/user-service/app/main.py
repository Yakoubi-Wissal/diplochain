from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.config import settings
from routers import users, roles, auth

app = FastAPI(
    title="DiploChain User Service",
    version="1.0.0",
    description="Manages users, roles, and authentication mappings",
)

from core.database import init_db

@app.on_event("startup")
async def on_startup():
    # ensure tables exist
    await init_db()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router)
app.include_router(roles.router)
app.include_router(auth.router)
