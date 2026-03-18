from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import dashboard

app = FastAPI(
    title="DiploChain Admin Dashboard Service",
    version="1.0.0",
    description="V6 Dashboard API for Super Admins"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(dashboard.router)

@app.on_event("startup")
async def on_startup():
    from core.database import init_db
    await init_db()


