from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from core.database import AsyncSessionLocal
from core.models import DashboardMetricsDaily, InstitutionStatistics, StudentStatistics, StabilityHistory
from core.schemas import DashboardMetricsRead, StabilityScoreRead

router = APIRouter(prefix="", tags=["Analytics"])

async def get_db():
    async with AsyncSessionLocal() as s:
        yield s

@router.get("/health", tags=["Health"])
async def health():
    return {"status": "ok"}

@router.get("/metrics/daily", response_model=list[DashboardMetricsRead])
async def list_daily_metrics(db: AsyncSession = Depends(get_db)):
    from sqlalchemy import select
    result = await db.execute(select(DashboardMetricsDaily))
    return result.scalars().all()

@router.get("/metrics/stability/history")
async def get_stability_history(db: AsyncSession = Depends(get_db)):
    from sqlalchemy import select
    result = await db.execute(select(StabilityHistory).order_by(StabilityHistory.timestamp.desc()).limit(10))
    return result.scalars().all()

@router.post("/security/scan")
async def receive_security_scan(scan: dict):
    # Process scan findings and update security scores
    logger.info(f"Received security scan findings: {len(scan.get('findings', []))}")
    return {"status": "processed"}

@router.get("/metrics/stability", response_model=StabilityScoreRead)
async def get_stability_metrics():
    # In a real system, these would be computed from audit_log and anomaly data
    # Here we simulate the dynamic nature based on hypothetical recent anomalies
    stability = 94.5
    security = 88.0

    return {
        "stability": stability,
        "security": security,
        "network": 99.2,
        "anomaly": 92.0,
        "recommendations": [
            "Upgrade user-service dependency 'httpx' to 0.27+",
            "Enable IPFS garbage collection to save 2.4GB"
        ]
    }
