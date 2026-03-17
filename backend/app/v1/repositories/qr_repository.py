from typing import Optional
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from models import QrCodeRecord
from .base import BaseRepository

class QrRepository(BaseRepository[QrCodeRecord]):
    def __init__(self, db: AsyncSession):
        super().__init__(QrCodeRecord, db)

    async def get_by_token(self, token: str) -> Optional[QrCodeRecord]:
        query = select(QrCodeRecord).where(QrCodeRecord.identifiant_opaque == token)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
