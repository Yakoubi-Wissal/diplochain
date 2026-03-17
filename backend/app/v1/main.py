import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.config import settings
from routers import auth, diplomes, institutions, specialites, users, dashboard, verification, departements, audit

# ── Application ───────────────────────────────────────────────────────────────
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="API Backend — Plateforme DiploChain : diplômes numériques sécurisés par blockchain",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── CORS ──────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(auth.router)
app.include_router(institutions.router)
app.include_router(specialites.router)
app.include_router(departements.router)
app.include_router(users.router)
app.include_router(diplomes.router)
app.include_router(dashboard.router)
app.include_router(verification.router)
app.include_router(audit.router)


# ── Scheduler (Retry Worker + metrics) ──────────────────────────────────────
from workers import retry_worker


@app.on_event("startup")
async def startup_event():
    # démarrer le scheduler de background (retry + métriques)
    if os.getenv("TESTING"):
        return
    try:
        retry_worker.start_scheduler()
    except Exception as e:
        # protect tests or broken loop
        import logging
        logging.getLogger(__name__).warning(f"scheduler start failed: {e}")


@app.on_event("shutdown")
async def shutdown_event():
    if os.getenv("TESTING"):
        return
    try:
        retry_worker.stop_scheduler()
    except Exception as e:
        import logging
        logging.getLogger(__name__).warning(f"scheduler stop failed: {e}")


# ── Santé ─────────────────────────────────────────────────────────────────────
@app.get("/", tags=["Santé"])
async def health_check():
    return {
        "status": "ok",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
    }
