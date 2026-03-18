from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import Optional

from core.database import AsyncSessionLocal
from core.models import Entreprise
from core.schemas import EntrepriseCreate, EntrepriseRead

router = APIRouter(prefix="", tags=["Entreprises"])

async def get_db():
    async with AsyncSessionLocal() as s:
        yield s

@router.get("/health", tags=["Health"])
async def health():
    return {"status": "ok"}

@router.post("/", response_model=EntrepriseRead)
async def create_entreprise(entreprise: EntrepriseCreate, db: AsyncSession = Depends(get_db)):
    db_entreprise = Entreprise(**entreprise.model_dump())
    db.add(db_entreprise)
    await db.commit()
    await db.refresh(db_entreprise)
    return db_entreprise

@router.get("/{entreprise_id}", response_model=EntrepriseRead)
async def read_entreprise(entreprise_id: int, db: AsyncSession = Depends(get_db)):
    entreprise = await db.get(Entreprise, entreprise_id)
    if not entreprise:
        raise HTTPException(status_code=404, detail="Entreprise not found")
    return entreprise

@router.get("/", response_model=list[EntrepriseRead])
async def search_entreprises(
    nom_entreprise: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    query_str = "SELECT * FROM entreprise"
    clauses = []
    params = {}
    if nom_entreprise:
        clauses.append("nom_entreprise ILIKE :nom")
        params["nom"] = f"%{nom_entreprise}%"
    
    if clauses:
        query_str += " WHERE " + " AND ".join(clauses)
    result = await db.execute(text(query_str), params)
    return result.mappings().all()
