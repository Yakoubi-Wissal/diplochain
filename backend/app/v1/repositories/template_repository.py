from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models import TemplateDepartement
from .base import BaseRepository

class TemplateRepository(BaseRepository[TemplateDepartement]):
    def __init__(self, db: AsyncSession):
        super().__init__(TemplateDepartement, db)

    async def list_by_institution(self, institution_id: Optional[int] = None) -> List[TemplateDepartement]:
        query = select(TemplateDepartement)
        if institution_id:
            query = query.where(TemplateDepartement.institution_id == institution_id)
        
        result = await self.db.execute(query.order_by(TemplateDepartement.nom))
        return result.scalars().all()
