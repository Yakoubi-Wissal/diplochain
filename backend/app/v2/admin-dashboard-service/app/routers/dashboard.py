from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import List, Optional

from core.database import AsyncSessionLocal
from core.models import DashboardMetricsDaily
from core.schemas import DashboardMetricsDailyRead

router = APIRouter(prefix="", tags=["Super Admin Dashboard"])

async def get_db():
    async with AsyncSessionLocal() as s:
        yield s

@router.get("/health", tags=["Health"])
async def health():
    return {"status": "healthy"}

@router.get("/metrics", response_model=List[DashboardMetricsDailyRead])
async def get_dashboard_metrics(db: AsyncSession = Depends(get_db)):
    from sqlalchemy import select
    result = await db.execute(
        select(DashboardMetricsDaily).order_by(DashboardMetricsDaily.metric_date.desc()).limit(30)
    )
    return result.scalars().all()

@router.get("/metrics/daily")
async def get_metrics_daily(db: AsyncSession = Depends(get_db)):
    # This can be a more complex aggregation if needed, for now return the same as metrics
    from sqlalchemy import select
    result = await db.execute(
        select(DashboardMetricsDaily).order_by(DashboardMetricsDaily.metric_date.asc()).limit(30)
    )
    return result.scalars().all()

@router.get("/diplomas")
async def list_diplomas_admin(db: AsyncSession = Depends(get_db)):
    result = await db.execute(text("SELECT * FROM diplome_blockchain_ext ORDER BY created_at DESC LIMIT 100"))
    return [dict(row) for row in result.mappings()]

@router.get("/students")
async def list_students_admin(db: AsyncSession = Depends(get_db)):
    result = await db.execute(text("SELECT * FROM etudiant ORDER BY nom LIMIT 100"))
    return [dict(row) for row in result.mappings()]

@router.get("/institutions")
async def list_institutions_admin(db: AsyncSession = Depends(get_db)):
    result = await db.execute(text("SELECT * FROM institution ORDER BY nom_institution LIMIT 100"))
    return [dict(row) for row in result.mappings()]
