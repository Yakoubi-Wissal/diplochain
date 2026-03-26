from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import List, Optional

from core.database import AsyncSessionLocal
from core.models import Institution, InstitutionBlockchainExt
from core.schemas import InstitutionCreate, InstitutionRead, InstitutionBlockchainRead, InstitutionBlockchainBase, InstitutionUpdate

router = APIRouter(prefix="", tags=["Institutions"])

async def get_db():
    async with AsyncSessionLocal() as s:
        yield s

@router.get("/health", tags=["Health"])
async def health():
    return {"status": "ok"}

@router.post("/", response_model=InstitutionRead, status_code=201)
async def create_institution(inst: InstitutionCreate, db: AsyncSession = Depends(get_db)):
    db_inst = Institution(**inst.model_dump())
    db.add(db_inst)
    await db.commit()
    await db.refresh(db_inst)
    return db_inst

@router.get("/", response_model=List[InstitutionRead])
async def list_institutions(active: Optional[bool] = None, db: AsyncSession = Depends(get_db)):
    query_str = "SELECT * FROM institution"
    params = {}
    if active is not None:
        query_str += " WHERE status = :s"
        params["s"] = "ACTIVE" if active else "ARCHIVEE"
    
    result = await db.execute(text(query_str), params)
    return result.mappings().all()

@router.get("/{institution_id}", response_model=InstitutionRead)
async def get_institution(institution_id: int, db: AsyncSession = Depends(get_db)):
    inst = await db.get(Institution, institution_id)
    if not inst:
        raise HTTPException(status_code=404, detail="Institution not found")
    return inst

@router.put("/{institution_id}", response_model=InstitutionRead)
async def update_institution(institution_id: int, inst: InstitutionUpdate, db: AsyncSession = Depends(get_db)):
    db_inst = await db.get(Institution, institution_id)
    if not db_inst:
        raise HTTPException(status_code=404, detail="Institution not found")
    for k, v in inst.model_dump(exclude_unset=True).items():
        setattr(db_inst, k, v)
    db.add(db_inst)
    await db.commit()
    await db.refresh(db_inst)
    return db_inst

@router.post("/{institution_id}/blockchain", response_model=InstitutionBlockchainRead)
async def add_blockchain_ext(institution_id: int, data: InstitutionBlockchainBase, db: AsyncSession = Depends(get_db)):
    entry = InstitutionBlockchainExt(institution_id=institution_id, **data.model_dump())
    db.add(entry)
    await db.commit()
    await db.refresh(entry)
    return entry

@router.get("/{institution_id}/students")
async def list_students_for_institution(institution_id: int):
    """Proxies request to student-service filtering by institution_id"""
    import httpx
    async with httpx.AsyncClient(timeout=5) as client:
        resp = await client.get(
            f"http://student-service:8000/students/search?institution_id={institution_id}"
        )
    return resp.json()
