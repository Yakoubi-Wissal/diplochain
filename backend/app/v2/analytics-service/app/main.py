from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import analytics

app = FastAPI(
    title="DiploChain Analytics Service",
    version="1.0.0",
    description="Dashboard metrics and statistics",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analytics.router)

@app.on_event("startup")
async def on_startup():
    from core.database import init_db
    await init_db()
