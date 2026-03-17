"""
routers/diplomes.py — DiploChain v6.0
Refactored for Core/Extension architecture.
"""

import hashlib
import io
import secrets
from datetime import date, datetime
from zoneinfo import ZoneInfo

TZ_TUNIS = ZoneInfo("Africa/Tunis")
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request, UploadFile, File, Form, status
from pydantic import BaseModel
from sqlalchemy import select, text, join
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from core.dependencies import get_current_user, require_role
from database import get_db
from models import (
    EtudiantDiplome, DiplomeBlockchainExt, HistoriqueOperation, 
    Institution, InstitutionBlockchainExt, QrCodeRecord, User, UserExt,
    StatutDiplome, TypeOperation
)

router = APIRouter(prefix="/diplomes", tags=["Diplômes"])


# ══════════════════════════════════════════════════════════════════════════════
#  SCHÉMAS LOCAUX (Ideally moved to schemas.py later)
# ══════════════════════════════════════════════════════════════════════════════

class DiplomeEmissionMicroservice(BaseModel):
    titre: str
    etudiant_id: str # Core etudiant_id is VARCHAR(10)
    institution_id: int
    specialite_id: Optional[str] = None
    mention: Optional[str] = None
    annee_promotion: Optional[str] = None


class DiplomeRevoke(BaseModel):
    commentaire: str


class DiplomeUpdate(BaseModel):
    titre: Optional[str] = None
    mention: Optional[str] = None
    specialite_id: Optional[str] = None
    annee_promotion: Optional[str] = None
    # allow status change only for revocation/original? Typically handled separately
    # If necessary, allow generation_mode but not risk
    generation_mode: Optional[str] = None


class DiplomeResponse(BaseModel):
    id_diplome: int
    titre: str
    mention: Optional[str]
    date_emission: date
    hash_sha256: str
    tx_id_fabric: Optional[str]
    ipfs_cid: str
    statut: str
    generation_mode: str
    blockchain_retry_count: int
    etudiant_id: str
    institution_id: int
    specialite_id: Optional[str]
    uploaded_by: int
    annee_promotion: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]


class HistoriqueResponse(BaseModel):
    id: int
    type_operation: str
    ancien_hash: Optional[str]
    nouvel_hash: str
    tx_id_fabric: str
    acteur_id: int
    ip_address: Optional[str]
    commentaire: Optional[str]
    timestamp: datetime


class VerificationResult(BaseModel):
    valid: bool
    diplome_id: Optional[int] = None
    etudiant_nom: Optional[str] = None
    etudiant_prenom: Optional[str] = None
    institution_nom: Optional[str] = None
    titre: Optional[str] = None
    date_emission: Optional[date] = None
    message: str


# ══════════════════════════════════════════════════════════════════════════════
#  ÉMISSION — MODE UPLOAD
# ══════════════════════════════════════════════════════════════════════════════

@router.post(
    "/emit/upload",
    response_model=DiplomeResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Émettre un diplôme — upload PDF direct",
)
async def emit_upload(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("ADMIN_INSTITUTION", "SUPER_ADMIN")),
    pdf_file: UploadFile = File(...),
    titre: str = Form(...),
    etudiant_id: str = Form(...),
    institution_id: int = Form(...),
    specialite_id: Optional[str] = Form(None),
    mention: Optional[str] = Form(None),
    annee_promotion: Optional[str] = Form(None),
    session_diplome: str = Form("Principale"),
    id_annexe: int = Form(1),
    num_diplome: int = Form(0),
    date_diplome: date = Form(date.today()),
    date_liv_diplome: date = Form(date.today()),
):
    if not pdf_file.content_type or "pdf" not in pdf_file.content_type.lower():
        raise HTTPException(status_code=400, detail="Le fichier doit être un PDF.")

    pdf_bytes = await pdf_file.read()
    if len(pdf_bytes) > 20 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="PDF trop volumineux (max 20 MB).")

    hash_sha256 = hashlib.sha256(pdf_bytes).hexdigest()

    return await _run_pipeline(
        db=db, admin=current_user, pdf_bytes=pdf_bytes,
        hash_sha256=hash_sha256, titre=titre,
        etudiant_id=etudiant_id, institution_id=institution_id,
        specialite_id=specialite_id, mention=mention,
        annee_promotion=annee_promotion,
        session_diplome=session_diplome, id_annexe=id_annexe,
        num_diplome=num_diplome, date_diplome=date_diplome,
        date_liv_diplome=date_liv_diplome,
        generation_mode="UPLOAD",
        client_ip=request.client.host if request.client else None,
    )


# ══════════════════════════════════════════════════════════════════════════════
#  ÉMISSION — MODE MICROSERVICE
# ══════════════════════════════════════════════════════════════════════════════

@router.post(
    "/emit/generate",
    response_model=DiplomeResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Émettre un diplôme — génération par microservice PDF",
)
async def emit_microservice(
    payload: DiplomeEmissionMicroservice,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("ADMIN_INSTITUTION", "SUPER_ADMIN")),
):
    # For now, default values for core fields
    session_diplome = "Principale"
    id_annexe = 1
    num_diplome = 0
    date_diplome = date.today()
    date_liv_diplome = date.today()

    try:
        from services.pdf_microservice import pdf_client
        pdf_bytes, hash_sha256 = await pdf_client.generate(
            titre=payload.titre,
            etudiant_id=payload.etudiant_id,
            institution_id=payload.institution_id,
            specialite_id=payload.specialite_id,
            mention=payload.mention,
            annee_promotion=payload.annee_promotion,
            db=db,
        )
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Microservice PDF indisponible : {e}")

    return await _run_pipeline(
        db=db, admin=current_user, pdf_bytes=pdf_bytes,
        hash_sha256=hash_sha256, titre=payload.titre,
        etudiant_id=payload.etudiant_id, institution_id=payload.institution_id,
        specialite_id=payload.specialite_id, mention=payload.mention,
        annee_promotion=payload.annee_promotion,
        session_diplome=session_diplome, id_annexe=id_annexe,
        num_diplome=num_diplome, date_diplome=date_diplome,
        date_liv_diplome=date_liv_diplome,
        generation_mode="MICROSERVICE",
        client_ip=request.client.host if request.client else None,
    )


# ══════════════════════════════════════════════════════════════════════════════
#  PIPELINE COMMUN
# ══════════════════════════════════════════════════════════════════════════════

async def _run_pipeline(
    db: AsyncSession, admin: User, pdf_bytes: bytes, hash_sha256: str,
    titre: str, etudiant_id: str, institution_id: int,
    specialite_id: Optional[str], mention: Optional[str],
    annee_promotion: Optional[str],
    session_diplome: str, id_annexe: int, num_diplome: int,
    date_diplome: date, date_liv_diplome: date,
    generation_mode: str,
    client_ip: Optional[str],
) -> DiplomeResponse:

    # Étape 1 : IPFS
    try:
        from services.ipfs_service import ipfs_service
        ipfs_cid = await ipfs_service.add_bytes(pdf_bytes)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Erreur IPFS : {e}")

    # Étape 2 : Core INSERT (EtudiantDiplome)
    core_diplome = EtudiantDiplome(
        etudiant_id=etudiant_id,
        session_diplome=session_diplome,
        id_annexe=id_annexe,
        num_diplome=num_diplome,
        date_diplome=date_diplome,
        date_liv_diplome=date_liv_diplome,
    )
    db.add(core_diplome)
    await db.flush() # Get id_diplome

    # Étape 3 : Extension INSERT (DiplomeBlockchainExt)
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
    db.add(ext_diplome)
    await db.flush()

    # Étape 4 : RegisterDiploma Fabric
    tx_id = None
    try:
        from services.fabric_service import fabric_service
        tx_id = await fabric_service.register_diploma(
            diplome_id=str(core_diplome.id_diplome),
            hash_sha256=hash_sha256,
            ipfs_cid=ipfs_cid,
            institution_id=str(institution_id),
            etudiant_id=etudiant_id,
            date_emission=str(date.today()),
        )
        # Étape 5 : UPDATE ORIGINAL
        ext_diplome.tx_id_fabric = tx_id
        ext_diplome.statut = StatutDiplome.ORIGINAL

    except Exception:
        # Fabric indisponible → PENDING_BLOCKCHAIN, le Retry Worker prendra le relais
        await db.commit()
        # ensure the extension object has all its generated/default
        # attributes populated before we leave the async context; calling
        # refresh loads columns that may have been expired on commit and
        # prevents _to_response from triggering an async load later.
        await db.refresh(ext_diplome)
        return _to_response(core_diplome, ext_diplome)

    # Étape 6 : QR Code
    token = secrets.token_urlsafe(32)
    verify_url = f"{settings.FRONTEND_URL}/verify/{token}"
    qr_path = f"/qr/{core_diplome.id_diplome}.png"

    db.add(QrCodeRecord(
        diplome_id=core_diplome.id_diplome,
        etudiant_id=etudiant_id,
        identifiant_opaque=token,
        url_verification=verify_url,
        qr_code_path=qr_path,
    ))

    # Étape 7 : Historique
    db.add(HistoriqueOperation(
        diplome_id=core_diplome.id_diplome,
        acteur_id=admin.id_user,
        type_operation=TypeOperation.EMISSION,
        nouvel_hash=hash_sha256,
        tx_id_fabric=tx_id,
        ip_address=client_ip,
    ))

    await db.commit()

    # Dashboard métriques (errors ignored to avoid blocking issuance)
    try:
        await db.execute(text("SELECT fn_refresh_dashboard_metrics(CURRENT_DATE)"))
        await db.commit()
    except Exception:
        pass

    # make sure the ext object is fresh - commit above will expire its
    # attributes by default, so we refresh now before handing back to
    # synchronous response conversion.
    await db.refresh(ext_diplome)

    return _to_response(core_diplome, ext_diplome)


# ══════════════════════════════════════════════════════════════════════════════
#  LISTE
# ══════════════════════════════════════════════════════════════════════════════

@router.get("/", response_model=List[DiplomeResponse])
async def list_diplomes(
    etudiant_id: Optional[str] = None,
    statut: Optional[str] = None,
    generation_mode: Optional[str] = Query(None, description="UPLOAD | MICROSERVICE"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = select(EtudiantDiplome, DiplomeBlockchainExt).join(
        DiplomeBlockchainExt, EtudiantDiplome.id_diplome == DiplomeBlockchainExt.id_diplome
    )

    # Check role and filter
    # For Student: only their own diplomas
    if current_user.ext.numero_etudiant: # Assuming current_user.ext is loaded
         query = query.where(EtudiantDiplome.etudiant_id == current_user.ext.numero_etudiant)
    elif etudiant_id:
        query = query.where(EtudiantDiplome.etudiant_id == etudiant_id)

    # For Institution Admin: only their institution
    if current_user.ext.institution_id:
        query = query.where(DiplomeBlockchainExt.institution_id == current_user.ext.institution_id)

    if statut:
        query = query.where(DiplomeBlockchainExt.statut == statut)
    if generation_mode:
        query = query.where(DiplomeBlockchainExt.generation_mode == generation_mode)

    result = await db.execute(query.order_by(DiplomeBlockchainExt.created_at.desc()))
    return [_to_response(row[0], row[1]) for row in result.all()]


@router.get("/mes-diplomes", response_model=List[DiplomeResponse])
async def mes_diplomes(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("ETUDIANT")),
):
    # Ensure UserExt is loaded or join it
    query = select(EtudiantDiplome, DiplomeBlockchainExt).join(
        DiplomeBlockchainExt, EtudiantDiplome.id_diplome == DiplomeBlockchainExt.id_diplome
    ).where(EtudiantDiplome.etudiant_id == current_user.ext.numero_etudiant)

    result = await db.execute(query.order_by(DiplomeBlockchainExt.date_emission.desc()))
    return [_to_response(row[0], row[1]) for row in result.all()]


@router.get("/{diplome_id}", response_model=DiplomeResponse)
async def get_diplome(
    diplome_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    core, ext = await _get_or_404(db, diplome_id)
    return _to_response(core, ext)


# ══════════════════════════════════════════════════════════════════════════════
#  RÉVOCATION
# ══════════════════════════════════════════════════════════════════════════════


@router.patch("/{diplome_id}", response_model=DiplomeResponse,
              summary="Met à jour certains champs d'un diplôme")
async def update_diplome(
    diplome_id: int,
    payload: DiplomeUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("ADMIN_INSTITUTION", "SUPER_ADMIN")),
):
    core, ext = await _get_or_404(db, diplome_id)
    # only allow updating select metadata
    if payload.titre is not None:
        ext.titre = payload.titre
    if payload.mention is not None:
        ext.mention = payload.mention
    if payload.specialite_id is not None:
        ext.specialite_id = payload.specialite_id
    if payload.annee_promotion is not None:
        ext.annee_promotion = payload.annee_promotion
    if payload.generation_mode is not None:
        ext.generation_mode = payload.generation_mode
    ext.updated_at = datetime.now(TZ_TUNIS).replace(tzinfo=None)
    await db.commit()
    return _to_response(core, ext)


@router.patch("/{diplome_id}/revoquer", response_model=DiplomeResponse)
async def revoquer_diplome(
    diplome_id: int,
    payload: DiplomeRevoke,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("ADMIN_INSTITUTION", "SUPER_ADMIN")),
):
    core, ext = await _get_or_404(db, diplome_id)

    if ext.statut == StatutDiplome.REVOQUE:
        raise HTTPException(status_code=400, detail="Diplôme déjà révoqué.")
    if ext.statut == StatutDiplome.PENDING_BLOCKCHAIN:
        raise HTTPException(status_code=400, detail="Impossible de révoquer un diplôme PENDING_BLOCKCHAIN.")

    try:
        from services.fabric_service import fabric_service
        tx_id = await fabric_service.revoke_diploma(str(diplome_id), payload.commentaire)
    except Exception:
        tx_id = f"TX_REVOC_{str(diplome_id).upper()}"

    ext.statut = StatutDiplome.REVOQUE
    ext.updated_at = datetime.now(TZ_TUNIS).replace(tzinfo=None)

    db.add(HistoriqueOperation(
        diplome_id=core.id_diplome,
        acteur_id=current_user.id_user,
        type_operation=TypeOperation.REVOCATION,
        ancien_hash=ext.hash_sha256,
        nouvel_hash=ext.hash_sha256,
        tx_id_fabric=tx_id,
        commentaire=payload.commentaire,
        ip_address=request.client.host if request.client else None,
    ))

    await db.commit()
    return _to_response(core, ext)


# ══════════════════════════════════════════════════════════════════════════════
#  VÉRIFICATION QR
# ══════════════════════════════════════════════════════════════════════════════

@router.get("/verify/{token}", response_model=VerificationResult)
async def verify_diplome(
    token: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("ENTREPRISE", "SUPER_ADMIN", "ADMIN_INSTITUTION")),
):
    qr_result = await db.execute(
        select(QrCodeRecord).where(QrCodeRecord.identifiant_opaque == token)
    )
    qr = qr_result.scalar_one_or_none()
    if not qr:
        return VerificationResult(valid=False, message="QR Code invalide ou révoqué.")

    # Source de vérité : Fabric
    try:
        from services.fabric_service import fabric_service
        fabric_data = await fabric_service.query_diploma(str(qr.diplome_id))
        hash_on_chain = fabric_data.get("hash_sha256", "")
        cid_on_chain = fabric_data.get("ipfs_cid", "")
    except Exception as e:
        return VerificationResult(valid=False, message=f"Fabric indisponible : {e}")

    if not hash_on_chain or not cid_on_chain:
        return VerificationResult(valid=False, message="Diplôme introuvable sur la blockchain.")

    # IPFS Sha check
    try:
        from services.ipfs_service import ipfs_service
        pdf_bytes = await ipfs_service.cat(cid_on_chain)
        recalculated = hashlib.sha256(pdf_bytes).hexdigest()
        valid = recalculated == hash_on_chain
    except Exception:
        valid = False # fallback if IPFS fails

    # Audit
    db.add(HistoriqueOperation(
        diplome_id=qr.diplome_id,
        acteur_id=current_user.id_user,
        type_operation=TypeOperation.VERIFICATION,
        nouvel_hash=hash_on_chain,
        tx_id_fabric=hash_on_chain,
        ip_address=request.client.host if request.client else None,
    ))
    await db.commit()

    if valid:
        core, ext = await _get_or_404(db, qr.diplome_id)
        # Fetch etudiant/institution details
        # For simplicity, returning what's in models.py
        # This part might need further joins for names
        return VerificationResult(
            valid=True,
            diplome_id=core.id_diplome,
            message="Diplôme authentique.",
        )

    return VerificationResult(valid=False, message="Hash invalide — diplôme potentiellement altéré.")


# ══════════════════════════════════════════════════════════════════════════════
#  HELPERS
# ══════════════════════════════════════════════════════════════════════════════

async def _get_or_404(db: AsyncSession, diplome_id: int) -> tuple[EtudiantDiplome, DiplomeBlockchainExt]:
    result = await db.execute(
        select(EtudiantDiplome, DiplomeBlockchainExt)
        .join(DiplomeBlockchainExt, EtudiantDiplome.id_diplome == DiplomeBlockchainExt.id_diplome)
        .where(EtudiantDiplome.id_diplome == diplome_id)
    )
    row = result.first()
    if not row:
        raise HTTPException(status_code=404, detail="Diplôme introuvable.")
    return row[0], row[1]


async def _get_user_or_404(db: AsyncSession, user_id: int) -> User:
    result = await db.execute(select(User).where(User.id_user == user_id))
    u = result.scalar_one_or_none()
    if not u:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable.")
    return u


async def _get_institution_or_404(db: AsyncSession, inst_id: int) -> Institution:
    result = await db.execute(select(Institution).where(Institution.institution_id == inst_id))
    i = result.scalar_one_or_none()
    if not i:
        raise HTTPException(status_code=404, detail="Institution introuvable.")
    return i


def _to_response(core: EtudiantDiplome, ext: DiplomeBlockchainExt) -> DiplomeResponse:
    return DiplomeResponse(
        id_diplome=core.id_diplome,
        titre=ext.titre,
        mention=ext.mention,
        date_emission=ext.date_emission,
        hash_sha256=ext.hash_sha256,
        tx_id_fabric=ext.tx_id_fabric,
        ipfs_cid=ext.ipfs_cid,
        statut=ext.statut,
        generation_mode=ext.generation_mode,
        blockchain_retry_count=ext.blockchain_retry_count,
        etudiant_id=core.etudiant_id,
        institution_id=ext.institution_id,
        specialite_id=ext.specialite_id,
        uploaded_by=ext.uploaded_by,
        annee_promotion=ext.annee_promotion,
        created_at=ext.created_at,
        updated_at=ext.updated_at,
    )
