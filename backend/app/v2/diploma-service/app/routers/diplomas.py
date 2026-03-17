from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from datetime import date

from core.database import AsyncSessionLocal
from core.models import Diploma, DiplomaStatusHistory
from core.schemas import DiplomaCreate, DiplomaRead, DiplomaUpdate

router = APIRouter(prefix="/diplomas", tags=["Diplomas"])

async def get_db():
    async with AsyncSessionLocal() as s:
        yield s

@router.get("/health", tags=["Health"])
async def health():
    return {"status": "ok"}

@router.post("/", response_model=DiplomaRead)
async def create_diploma(d: DiplomaCreate, db: AsyncSession = Depends(get_db)):
    dip = Diploma(**d.model_dump())
    db.add(dip)
    await db.commit()
    await db.refresh(dip)
    return dip

@router.get("/{diploma_id}", response_model=DiplomaRead)
async def read_diploma(diploma_id: UUID, db: AsyncSession = Depends(get_db)):
    dip = await db.get(Diploma, diploma_id)
    if not dip:
        raise HTTPException(status_code=404, detail="Diploma not found")
    return dip

@router.put("/{diploma_id}", response_model=DiplomaRead)
async def update_diploma(diploma_id: UUID, d: DiplomaUpdate, db: AsyncSession = Depends(get_db)):
    dip = await db.get(Diploma, diploma_id)
    if not dip:
        raise HTTPException(status_code=404, detail="Diploma not found")
    for k,v in d.model_dump(exclude_unset=True).items():
        setattr(dip, k, v)
    db.add(dip)
    await db.commit()
    await db.refresh(dip)
    return dip

@router.post("/{diploma_id}/revoke", response_model=DiplomaRead)
async def revoke_diploma(diploma_id: UUID, db: AsyncSession = Depends(get_db)):
    dip = await db.get(Diploma, diploma_id)
    if not dip:
        raise HTTPException(status_code=404, detail="Diploma not found")
    old = dip.statut
    dip.statut = "REVOQUE"
    db.add(dip)
    await db.commit()
    await db.refresh(dip)
    hist = DiplomaStatusHistory(
        diploma_id=diploma_id,
        old_status=old,
        new_status="REVOQUE",
        changed_at=date.today(),
    )
    db.add(hist)
    await db.commit()
    return dip
