from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from models import Institution
from .base import BaseRepository

class InstitutionRepository(BaseRepository[Institution]):
    def __init__(self, db: AsyncSession):
        super().__init__(Institution, db)

    async def get_with_blockchain(self, inst_id: int) -> Optional[Institution]:
        query = select(Institution).options(
            selectinload(Institution.blockchain_ext)
        ).where(Institution.institution_id == inst_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def list_active(self) -> List[Institution]:
        query = select(Institution).join(Institution.blockchain_ext).where(
            # Depending on if we want Core or Ext status, sticking to Ext as per dashboard logic
            True 
        )
        result = await self.db.execute(query)
        return result.scalars().all()
