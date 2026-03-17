from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.config import settings
from routers import institutions

app = FastAPI(
    title="DiploChain Institution Service",
    version="1.0.0",
    description="Manage institutions and related metadata",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(institutions.router)

@app.on_event("startup")
async def on_startup():
    from core.database import init_db
    await init_db()
