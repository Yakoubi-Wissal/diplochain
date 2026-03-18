from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select
from datetime import date

from core.database import AsyncSessionLocal
from core.models import EtudiantDiplome, DiplomeBlockchainExt, HistoriqueOperations
from core.schemas import DiplomaCreate, DiplomaRead, DiplomaUpdate

router = APIRouter(prefix="", tags=["Diplomas"])

async def get_db():
    async with AsyncSessionLocal() as s:
        yield s

@router.get("/health", tags=["Health"])
async def health():
    return {"status": "ok"}

@router.post("/", response_model=DiplomaRead)
async def create_diploma(d: DiplomaCreate, db: AsyncSession = Depends(get_db)):
    # 1. Create core record
    core_dip = EtudiantDiplome(
        etudiant_id=d.etudiant_id,
        session_diplome=d.session_diplome,
        id_annexe=d.id_annexe,
        num_diplome=d.num_diplome,
        date_diplome=d.date_diplome,
        date_liv_diplome=d.date_liv_diplome,
    )
    db.add(core_dip)
    await db.flush()  # to get id_diplome

    # 2. Create blockchain ext record
    ext_dip = DiplomeBlockchainExt(
        id_diplome=core_dip.id_diplome,
        titre=d.titre,
        mention=d.mention,
        date_emission=d.date_emission,
        annee_promotion=d.annee_promotion,
        hash_sha256=d.hash_sha256,
        ipfs_cid=d.ipfs_cid,
        statut=d.statut,
        generation_mode=d.generation_mode,
        template_id=d.template_id,
        institution_id=d.institution_id,
        specialite_id=d.specialite_id,
        uploaded_by=d.uploaded_by,
    )
    db.add(ext_dip)
    
    # 3. Create history record
    hist = HistoriqueOperations(
        diplome_id=core_dip.id_diplome,
        type_operation="EMISSION",
        nouvel_hash=d.hash_sha256,
        tx_id_fabric="PENDING",
        acteur_id=d.uploaded_by,
        commentaire="Initial emission",
    )
    db.add(hist)
    
    await db.commit()
    
    # Reload with joined data
    res = await db.execute(select(EtudiantDiplome).options(selectinload(EtudiantDiplome.blockchain_ext)).filter_by(id_diplome=core_dip.id_diplome))
    dip = res.scalar_one()
    
    # Merge into a single dict for Pydantic
    merged = {**dip.__dict__, **dip.blockchain_ext.__dict__}
    return merged

@router.get("/", response_model=List[DiplomaRead])
async def list_diplomas(db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(EtudiantDiplome).options(selectinload(EtudiantDiplome.blockchain_ext)))
    diplomas = []
    for dip in res.scalars().all():
        if dip.blockchain_ext:
            diplomas.append({**dip.__dict__, **dip.blockchain_ext.__dict__})
    return diplomas

@router.get("/{diploma_id}") # Removed response_model to prevent dict validation errors from union
async def read_diploma(diploma_id: int, db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(EtudiantDiplome).options(selectinload(EtudiantDiplome.blockchain_ext)).filter_by(id_diplome=diploma_id))
    dip = res.scalar_one_or_none()
    if not dip:
        raise HTTPException(status_code=404, detail="Diploma not found")
    if not dip.blockchain_ext:
        return dip.__dict__
    return {**dip.__dict__, **dip.blockchain_ext.__dict__}

@router.put("/{diploma_id}")
async def update_diploma(diploma_id: int, d: DiplomaUpdate, db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(DiplomeBlockchainExt).filter_by(id_diplome=diploma_id))
    ext = res.scalar_one_or_none()
    if not ext:
        raise HTTPException(status_code=404, detail="Diploma metadata not found")
        
    for k, v in d.model_dump(exclude_unset=True).items():
        setattr(ext, k, v)
        
    db.add(ext)
    await db.commit()
    
    res_full = await db.execute(select(EtudiantDiplome).options(selectinload(EtudiantDiplome.blockchain_ext)).filter_by(id_diplome=diploma_id))
    dip = res_full.scalar_one()
    return {**dip.__dict__, **dip.blockchain_ext.__dict__}

@router.post("/{diploma_id}/revoke")
async def revoke_diploma(diploma_id: int, user_id: int = 1, db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(DiplomeBlockchainExt).filter_by(id_diplome=diploma_id))
    ext = res.scalar_one_or_none()
    if not ext:
        raise HTTPException(status_code=404, detail="Diploma not found")
        
    old_hash = ext.hash_sha256
    ext.statut = "REVOQUE"
    db.add(ext)
    
    hist = HistoriqueOperations(
        diplome_id=diploma_id,
        type_operation="REVOCATION",
        ancien_hash=old_hash,
        nouvel_hash=old_hash, # hash stays the same, status changes on-chain
        tx_id_fabric="PENDING_REVOKE",
        acteur_id=user_id,
        commentaire="Revocation by admin",
    )
    db.add(hist)
    
    await db.commit()
    
    res_full = await db.execute(select(EtudiantDiplome).options(selectinload(EtudiantDiplome.blockchain_ext)).filter_by(id_diplome=diploma_id))
    dip = res_full.scalar_one()
    return {**dip.__dict__, **dip.blockchain_ext.__dict__}
