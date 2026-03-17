import logging
import secrets
from datetime import date, datetime
from zoneinfo import ZoneInfo
from typing import Optional

# timezone used for any manual timestamps
TZ_TUNIS = ZoneInfo("Africa/Tunis")

from fastapi import HTTPException
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from models import (
    StatutDiplome,
    EtudiantDiplome,
    DiplomeBlockchainExt,
    QrCodeRecord,
    HistoriqueOperation,
    TypeOperation,
    User
)
from repositories.diploma_repository import DiplomaRepository
from repositories.qr_repository import QrRepository
from repositories.history_repository import HistoryRepository
from services.blockchain_client import blockchain_client
from services.ipfs_service import ipfs_service

logger = logging.getLogger(__name__)

class DiplomaService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.diploma_repo = DiplomaRepository(db)
        self.qr_repo = QrRepository(db)
        self.history_repo = HistoryRepository(db)

    async def emit_diploma(
        self,
        admin: User,
        pdf_bytes: bytes,
        hash_sha256: str,
        titre: str,
        etudiant_id: str,
        institution_id: int,
        specialite_id: Optional[str],
        mention: Optional[str],
        annee_promotion: Optional[str],
        session_diplome: str,
        id_annexe: int,
        num_diplome: int,
        date_diplome: date,
        date_liv_diplome: date,
        generation_mode: str,
        client_ip: Optional[str] = None,
    ) -> tuple[EtudiantDiplome, DiplomeBlockchainExt]:
        """
        Full Emission Pipeline:
        1. IPFS Upload
        2. Insert EtudiantDiplome (Core)
        3. Insert DiplomeBlockchainExt (Extension)
        4. Register on Blockchain (Fabric)
        5. Create QR Code Record
        6. Record Operation History
        7. Refresh Dashboard Metrics
        """
        
        # 1. IPFS
        try:
            ipfs_cid = await ipfs_service.add_bytes(pdf_bytes)
        except Exception as e:
            logger.error(f"IPFS Error: {e}")
            raise HTTPException(status_code=502, detail=f"Erreur IPFS : {e}")

        # 2. Core INSERT
        core_diplome = EtudiantDiplome(
            etudiant_id=etudiant_id,
            session_diplome=session_diplome,
            id_annexe=id_annexe,
            num_diplome=num_diplome,
            date_diplome=date_diplome,
            date_liv_diplome=date_liv_diplome,
        )
        self.db.add(core_diplome)
        await self.db.flush() # Get id_diplome

        # 3. Extension INSERT
        ext_diplome = DiplomeBlockchainExt(
            id_diplome=core_diplome.id_diplome,
            titre=titre,
            mention=mention,
            date_emission=date.today(),
            annee_promotion=annee_promotion,
            hash_sha256=hash_sha256,
            ipfs_cid=ipfs_cid,
            tx_id_fabric=None,
            statut=StatutDiplome.PENDING_BLOCKCHAIN,
            generation_mode=generation_mode,
            institution_id=institution_id,
            specialite_id=specialite_id,
            uploaded_by=admin.id_user,
            blockchain_retry_count=0,
        )
        self.db.add(ext_diplome)
        await self.db.flush()

        # 4. Fabric Registration
        tx_id = None
        try:
            tx_id = await blockchain_client.register_diploma_hash(hash_sha256)
            ext_diplome.tx_id_fabric = tx_id
            # maintain legacy status value for compatibility with existing
            # frontend/queries that expect ORIGINAL.
            ext_diplome.statut = StatutDiplome.ORIGINAL
        except Exception as e:
            logger.warning(f"Blockchain registration failed: {e}")
            # Keep as PENDING_BLOCKCHAIN, Retry Worker will handle it

        # 5. QR Code
        # QR code simply encodes the public diploma identifier
        verify_url = f"{settings.FRONTEND_URL}/verify/{core_diplome.id_diplome}"
        qr_path = f"/qr/{core_diplome.id_diplome}.png"

        self.db.add(QrCodeRecord(
            diplome_id=core_diplome.id_diplome,
            etudiant_id=etudiant_id,
            identifiant_opaque=str(core_diplome.id_diplome),
            url_verification=verify_url,
            qr_code_path=qr_path,
        ))

        # 6. Historique
        self.db.add(HistoriqueOperation(
            diplome_id=core_diplome.id_diplome,
            acteur_id=admin.id_user,
            type_operation=TypeOperation.EMISSION,
            nouvel_hash=hash_sha256,
            tx_id_fabric=tx_id or "PENDING",
            ip_address=client_ip,
        ))

        await self.db.commit()

        # 7. Dashboard Metrics Refresh
        try:
            await self.db.execute(text("SELECT fn_refresh_dashboard_metrics(CURRENT_DATE)"))
            await self.db.commit()
        except Exception:
            pass # Non-critical failure

        # refresh core & extension objects before returning to avoid
        # lazy-load issues (eg. MissingGreenlet during tests)
        await self.db.refresh(core_diplome)
        await self.db.refresh(ext_diplome)
        # return both so caller can serialize without triggering further DB IO
        return core_diplome, ext_diplome

    async def verify_token(self, token: str, actor: Optional[User] = None, client_ip: Optional[str] = None) -> Optional[EtudiantDiplome]:
        qr = await self.qr_repo.get_by_token(token)
        if not qr:
            return None
        
        diploma = await self.diploma_repo.get_with_ext(qr.diplome_id)
        if not diploma:
            return None

        # Audit
        if actor:
            self.db.add(HistoriqueOperation(
                diplome_id=diploma.id_diplome,
                acteur_id=actor.id_user,
                type_operation=TypeOperation.VERIFICATION,
                nouvel_hash=diploma.blockchain_ext.hash_sha256,
                tx_id_fabric=diploma.blockchain_ext.tx_id_fabric or "N/A",
                ip_address=client_ip,
            ))
            await self.db.commit()

        return diploma

    async def revoke_diploma(self, diplome_id: int, actor: User, commentaire: str, client_ip: Optional[str] = None) -> EtudiantDiplome:
        """
        Revocation Pipeline:
        1. Blockchain Revocation
        2. Database Status Update
        3. Record History
        """
        # load diploma with extension data
        diploma = await self.diploma_repo.get_with_ext(diplome_id)
        if not diploma or not diploma.blockchain_ext:
            raise HTTPException(status_code=404, detail="Diplôme introuvable.")

        ext = diploma.blockchain_ext
        if ext.statut == StatutDiplome.REVOQUE:
            raise HTTPException(status_code=400, detail="Diplôme déjà révoqué.")
        if ext.statut == StatutDiplome.PENDING_BLOCKCHAIN:
            raise HTTPException(
                status_code=400,
                detail="Impossible de révoquer un diplôme en attente de confirmation blockchain."
            )

        # 1. Blockchain
        try:
            tx_id = await blockchain_client.revoke_diploma(ext.tx_id_fabric)
        except Exception as e:
            logger.error(f"Blockchain Revocation Error: {e}")
            tx_id = f"REVOKE_FALLBACK_{secrets.token_hex(4)}"

        # 2. Database
        ext.statut = StatutDiplome.REVOQUE
        ext.updated_at = datetime.now(TZ_TUNIS).replace(tzinfo=None)

        # 3. History
        self.db.add(HistoriqueOperation(
            diplome_id=diplome_id,
            acteur_id=actor.id_user,
            type_operation=TypeOperation.REVOCATION,
            ancien_hash=ext.hash_sha256,
            nouvel_hash=ext.hash_sha256,
            tx_id_fabric=tx_id,
            commentaire=commentaire,
            ip_address=client_ip,
        ))

        await self.db.commit()
        await self.db.refresh(diploma)
        return diploma
