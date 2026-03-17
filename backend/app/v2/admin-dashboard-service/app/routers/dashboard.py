from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import List, Optional

from core.database import AsyncSessionLocal
from core.models import DashboardMetricsDaily
from core.schemas import DashboardMetricsDailyRead

router = APIRouter(prefix="/admin", tags=["Super Admin Dashboard"])

async def get_db():
    async with AsyncSessionLocal() as s:
        yield s

@router.get("/health", tags=["Health"])
async def health():
    return {"status": "ok"}

@router.get("/dashboard", response_model=List[DashboardMetricsDailyRead])
async def get_dashboard_metrics(
    period: Optional[str] = "today", 
    db: AsyncSession = Depends(get_db)
):
    # In a real impl, period affects the WHERE clause.
    query = "SELECT * FROM dashboard_metrics_daily ORDER BY metric_date DESC LIMIT 30"
    result = await db.execute(text(query))
    return result.scalars().all()

@router.get("/diplomas")
async def list_diplomas_admin(db: AsyncSession = Depends(get_db)):
    # Mocking returning diplomas 
    return [{"message": "List of diplomas for admin view"}]

@router.get("/students")
async def list_students_admin(db: AsyncSession = Depends(get_db)):
    # Mocking returning students
    return [{"message": "List of students for admin view"}]

@router.get("/institutions")
async def list_institutions_admin(db: AsyncSession = Depends(get_db)):
    # Mocking returning institutions
    return [{"message": "List of institutions for admin view"}]
