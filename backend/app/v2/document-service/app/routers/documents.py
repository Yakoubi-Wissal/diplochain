from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import List, Optional

from core.database import AsyncSessionLocal
from core.models import Rapport, RapportInstitution

router = APIRouter(prefix="/rapports", tags=["Rapports"])

async def get_db():
    async with AsyncSessionLocal() as s:
        yield s

@router.get("/health", tags=["Health"])
async def health():
    return {"status": "ok"}

@router.post("/", response_model=dict)
async def create_rapport(rapport: dict, db: AsyncSession = Depends(get_db)):
    # expecting full dict matching Rapport fields
    r = Rapport(**rapport)
    db.add(r)
    await db.commit()
    await db.refresh(r)
    return {"id_rapport": r.id_rapport}

@router.get("/{id_rapport}", response_model=dict)
async def read_rapport(id_rapport: int, db: AsyncSession = Depends(get_db)):
    r = await db.get(Rapport, id_rapport)
    if not r:
        raise HTTPException(status_code=404, detail="Rapport not found")
    return r.__dict__

@router.get("/", response_model=List[dict])
async def list_rapports(code: Optional[str] = None, db: AsyncSession = Depends(get_db)):
    query_str = "SELECT * FROM rapport"
    params = {}
    if code:
        query_str += " WHERE code_rapport = :c"
        params["c"] = code
    result = await db.execute(text(query_str), params)
    return [row._mapping for row in result]
