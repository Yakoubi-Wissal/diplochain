from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from core.database import AsyncSessionLocal
from core.models import DashboardMetricsDaily, InstitutionStatistics, StudentStatistics
from core.schemas import DashboardMetricsRead

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

@router.get("/metrics/realtime")
async def get_realtime_metrics(db: AsyncSession = Depends(get_db)):
    # Simulating aggregation of real-time performance and error data
    # In production, this would query a dedicated metrics table or Prometheus
    return {
        "stability_score": 99.1,
        "error_rate": 0.35,
        "avg_latency": 118,
        "active_users": 15,
        "total_tx": 158,
        "diplomas": 92,
        "verifications": 48,
        "revocations": 3
    }
