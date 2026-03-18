from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import List, Optional

from core.database import AsyncSessionLocal
from core.models import Rapport, RapportInstitution
from core.schemas import RapportCreate, RapportRead

router = APIRouter(prefix="", tags=["Rapports"])

async def get_db():
    async with AsyncSessionLocal() as s:
        yield s

@router.get("/health", tags=["Health"])
async def health():
    return {"status": "ok"}

@router.post("/", response_model=RapportRead)
async def create_rapport(rapport: RapportCreate, db: AsyncSession = Depends(get_db)):
    r = Rapport(**rapport.model_dump())
    db.add(r)
    await db.commit()
    await db.refresh(r)
    return r

@router.get("/{id_rapport}", response_model=RapportRead)
async def read_rapport(id_rapport: int, db: AsyncSession = Depends(get_db)):
    r = await db.get(Rapport, id_rapport)
    if not r:
        raise HTTPException(status_code=404, detail="Rapport not found")
    return r

@router.get("/", response_model=List[RapportRead])
async def list_rapports(code: Optional[str] = None, db: AsyncSession = Depends(get_db)):
    query_str = "SELECT * FROM rapport"
    params = {}
    if code:
        query_str += " WHERE code_rapport = :c"
        params["c"] = code
    result = await db.execute(text(query_str), params)
    return result.mappings().all()
