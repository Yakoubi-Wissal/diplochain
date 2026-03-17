from datetime import date
from typing import List, Optional
from sqlalchemy import select, func, text
from sqlalchemy.ext.asyncio import AsyncSession
from models import DashboardMetricsDaily
from .base import BaseRepository

class DashboardRepository(BaseRepository[DashboardMetricsDaily]):
    def __init__(self, db: AsyncSession):
        super().__init__(DashboardMetricsDaily, db)

    async def get_latest_metrics(self) -> Optional[DashboardMetricsDaily]:
        query = select(DashboardMetricsDaily).order_by(DashboardMetricsDaily.metric_date.desc()).limit(1)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_students_stats(self) -> List[dict]:
        result = await self.db.execute(text("SELECT * FROM v_diplomas_per_student"))
        return result.mappings().all()

    async def get_institutions_stats(self) -> List[dict]:
        result = await self.db.execute(text("SELECT * FROM v_diplomas_per_institution"))
        return result.mappings().all()

    async def refresh_metrics(self, d: Optional[date] = None):
        target = d or date.today()
        # Calls the SQL function fn_refresh_dashboard_metrics()
        await self.db.execute(text("SELECT fn_refresh_dashboard_metrics(:d)"), {"d": target})
        await self.db.commit()
