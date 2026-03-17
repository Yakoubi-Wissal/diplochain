from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from models import EtudiantDiplome, DiplomeBlockchainExt
from .base import BaseRepository

class DiplomaRepository(BaseRepository[EtudiantDiplome]):
    def __init__(self, db: AsyncSession):
        super().__init__(EtudiantDiplome, db)

    async def get_with_ext(self, diploma_id: int) -> Optional[EtudiantDiplome]:
        query = select(EtudiantDiplome).options(
            selectinload(EtudiantDiplome.blockchain_ext)
        ).where(EtudiantDiplome.id_diplome == diploma_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def list_filtered(
        self,
        etudiant_id: Optional[str] = None,
        institution_id: Optional[int] = None,
        statut: Optional[str] = None,
        generation_mode: Optional[str] = None,
        limit: int = 100
    ) -> List[EtudiantDiplome]:
        query = select(EtudiantDiplome).options(
            selectinload(EtudiantDiplome.blockchain_ext)
        ).join(EtudiantDiplome.blockchain_ext)

        if etudiant_id:
            query = query.where(EtudiantDiplome.etudiant_id == etudiant_id)
        if institution_id:
            query = query.where(DiplomeBlockchainExt.institution_id == institution_id)
        if statut:
            query = query.where(DiplomeBlockchainExt.statut == statut)
        if generation_mode:
            query = query.where(DiplomeBlockchainExt.generation_mode == generation_mode)

        query = query.order_by(DiplomeBlockchainExt.created_at.desc()).limit(limit)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def list_pending(self, limit: int = 20) -> List[EtudiantDiplome]:
        query = select(EtudiantDiplome).join(EtudiantDiplome.blockchain_ext).where(
            DiplomeBlockchainExt.statut == 'PENDING_BLOCKCHAIN'
        ).limit(limit)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_by_hash(self, hash_sha256: str) -> Optional[EtudiantDiplome]:
        query = select(EtudiantDiplome).join(EtudiantDiplome.blockchain_ext).where(
            DiplomeBlockchainExt.hash_sha256 == hash_sha256
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
