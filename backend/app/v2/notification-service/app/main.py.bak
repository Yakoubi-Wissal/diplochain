from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import notifications

app = FastAPI(
    title="DiploChain Notification Service",
    version="1.0.0",
    description="Handles sending and logging notifications",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(notifications.router)

@app.on_event("startup")
async def on_startup():
    from core.database import init_db
    await init_db()


