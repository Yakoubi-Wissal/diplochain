from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import entreprises

app = FastAPI(
    title="DiploChain Entreprise Service",
    version="1.0.0",
    description="Handles company/employer profiles",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(entreprises.router)

@app.on_event("startup")
async def on_startup():
    from core.database import init_db
    await init_db()
