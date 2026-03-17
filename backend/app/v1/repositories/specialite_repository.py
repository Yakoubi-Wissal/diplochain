from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from models import Specialite, SpecialiteExt
from .base import BaseRepository

class SpecialiteRepository(BaseRepository[Specialite]):
    def __init__(self, db: AsyncSession):
        super().__init__(Specialite, db)

    async def get_with_ext(self, code: str) -> Optional[Specialite]:
        query = select(Specialite).options(
            selectinload(Specialite.ext)
        ).where(Specialite.code_specialite == code)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def list_by_institution(self, institution_id: int) -> List[Specialite]:
        query = select(Specialite).join(Specialite.ext).where(
            SpecialiteExt.institution_id == institution_id
        ).options(selectinload(Specialite.ext))
        result = await self.db.execute(query)
        return result.scalars().all()
