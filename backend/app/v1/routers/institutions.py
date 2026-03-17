"""
routers/institutions.py — DiploChain v6.0
Refactored for Core/Extension architecture.
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from core.dependencies import get_current_user, require_role
from database import get_db
from repositories.institution_repository import InstitutionRepository
from models import Institution, InstitutionBlockchainExt, StatutInstitution, User
from schemas import InstitutionRead # Assuming InstitutionRead handles the combined view

router = APIRouter(prefix="/institutions", tags=["Institutions"])


@router.get("/", response_model=List[InstitutionRead])
async def list_institutions(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_role("SUPER_ADMIN")),
):
    query = select(Institution).options(selectinload(Institution.blockchain_ext))
    result = await db.execute(query.order_by(Institution.nom_institution))
    return [_to_institution_read(i) for i in result.scalars().all()]


@router.post("/", response_model=InstitutionRead, status_code=status.HTTP_201_CREATED)
async def create_institution(
    nom_institution: str,
    code: Optional[str] = None,
    channel_id: Optional[str] = None,
    peer_node_url: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_role("SUPER_ADMIN")),
):
    inst = Institution(nom_institution=nom_institution)
    db.add(inst)
    await db.flush()
    # extension
    if code or channel_id or peer_node_url:
        ext = InstitutionBlockchainExt(
            institution_id=inst.institution_id,
            code=code,
            channel_id=channel_id,
            peer_node_url=peer_node_url,
        )
        db.add(ext)
    await db.commit()
    await db.refresh(inst)
    return _to_institution_read(inst)


@router.get("/{institution_id}", response_model=InstitutionRead)
async def get_institution(
    institution_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_role("SUPER_ADMIN", "ADMIN_INSTITUTION")),
):
    result = await db.execute(
        select(Institution).options(selectinload(Institution.blockchain_ext))
        .where(Institution.institution_id == institution_id)
    )
    institution = result.scalar_one_or_none()
    if not institution:
        raise HTTPException(status_code=404, detail="Institution introuvable.")
    return _to_institution_read(institution)


@router.patch("/{institution_id}", response_model=InstitutionRead)
async def update_institution(
    institution_id: int,
    nom_institution: Optional[str] = None,
    code: Optional[str] = None,
    status: Optional[StatutInstitution] = None,
    channel_id: Optional[str] = None,
    peer_node_url: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_role("SUPER_ADMIN")),
):
    result = await db.execute(
        select(Institution).options(selectinload(Institution.blockchain_ext))
        .where(Institution.institution_id == institution_id)
    )
    institution = result.scalar_one_or_none()
    if not institution:
        raise HTTPException(status_code=404, detail="Institution introuvable.")

    if nom_institution is not None:
        institution.nom_institution = nom_institution
    if channel_id is not None or peer_node_url is not None or code is not None or status is not None:
        if not institution.blockchain_ext:
            institution.blockchain_ext = InstitutionBlockchainExt(institution_id=institution.institution_id)
        if code is not None:
            institution.blockchain_ext.code = code
        if channel_id is not None:
            institution.blockchain_ext.channel_id = channel_id
        if peer_node_url is not None:
            institution.blockchain_ext.peer_node_url = peer_node_url
        if status is not None:
            institution.blockchain_ext.status = status

    await db.commit()
    await db.refresh(institution)
    return _to_institution_read(institution)


# Helper conversion
def _to_institution_read(i: Institution) -> InstitutionRead:
    return InstitutionRead(
        institution_id=i.institution_id,
        nom_institution=i.nom_institution,
        code=i.blockchain_ext.code if i.blockchain_ext else None,
        status=i.blockchain_ext.status if i.blockchain_ext else "ACTIVE",
        channel_id=i.blockchain_ext.channel_id if i.blockchain_ext else None,
        peer_node_url=i.blockchain_ext.peer_node_url if i.blockchain_ext else None,
    )
