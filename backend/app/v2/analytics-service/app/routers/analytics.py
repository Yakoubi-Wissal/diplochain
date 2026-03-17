from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from core.database import AsyncSessionLocal
from core.models import DashboardMetricsDaily, InstitutionStatistics, StudentStatistics
from core.schemas import DashboardMetricsRead

router = APIRouter(prefix="/analytics", tags=["Analytics"])

async def get_db():
    async with AsyncSessionLocal() as s:
        yield s

@router.get("/health", tags=["Health"])
async def health():
    return {"status": "ok"}

@router.get("/metrics/daily", response_model=list[DashboardMetricsRead])
async def list_daily_metrics(db: AsyncSession = Depends(get_db)):
    result = await db.execute(text("SELECT * FROM dashboard_metrics_daily"))
    return result.scalars().all()
