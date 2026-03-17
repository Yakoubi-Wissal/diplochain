from sqlalchemy.ext.asyncio import AsyncSession
from models import HistoriqueOperation
from .base import BaseRepository

class HistoryRepository(BaseRepository[HistoriqueOperation]):
    def __init__(self, db: AsyncSession):
        super().__init__(HistoriqueOperation, db)
