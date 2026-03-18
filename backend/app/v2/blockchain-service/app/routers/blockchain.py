from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text,select
from typing import List, Optional
from datetime import date

from core.database import AsyncSessionLocal
from core.models import DiplomaBlockchain
from core.schemas import DiplomaBlockchainRead, DiplomaBlockchainCreate

router = APIRouter(prefix="", tags=["Blockchain"])

async def get_db():
    async with AsyncSessionLocal() as s:
        yield s

@router.get("/health", tags=["Health"])
async def health():
    return {"status": "ok"}

@router.post("/diplome", response_model=DiplomaBlockchainRead)
async def record_blockchain(d: DiplomaBlockchainCreate, db: AsyncSession = Depends(get_db)):
    obj = DiplomaBlockchain(**d.model_dump())
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return obj

@router.get("/diplome/{id_diplome}", response_model=DiplomaBlockchainRead)
async def get_blockchain(id_diplome: int, db: AsyncSession = Depends(get_db)):
    obj = await db.get(DiplomaBlockchain, id_diplome)
    if not obj:
        raise HTTPException(status_code=404, detail="Record not found")
    return obj

@router.get("/diplomes", response_model=List[DiplomaBlockchainRead])
async def list_blockchain(institution_id: Optional[int] = None, db: AsyncSession = Depends(get_db)):
    from sqlalchemy import select
    query = select(DiplomaBlockchain)
    if institution_id is not None:
        query = query.where(DiplomaBlockchain.institution_id == institution_id)
    result = await db.execute(query)
    return result.scalars().all()
