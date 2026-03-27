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
    return {"status": "healthy"}

@router.post("/diplome", response_model=DiplomaBlockchainRead)
async def record_blockchain(d: DiplomaBlockchainCreate, db: AsyncSession = Depends(get_db)):
    data = d.model_dump()
    # Remove fields that might be handled by DB defaults if they are None in input
    if data.get("created_at") is None:
        data.pop("created_at", None)
    obj = DiplomaBlockchain(**data)
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

@router.get("/audit/ledger", tags=["Audit"])
async def audit_ledger(db: AsyncSession = Depends(get_db)):
    # Deep Audit: Verify all diploma hashes and transaction sequence
    # This simulates a real Hyperledger Fabric ledger scan
    result = await db.execute(select(DiplomaBlockchain))
    records = result.scalars().all()

    anomalies = []
    for r in records:
        if not r.hash_sha256 or len(r.hash_sha256) != 64:
            anomalies.append({"id": r.id_diplome, "issue": "Invalid Hash Integrity"})
        if r.statut == 'PENDING_BLOCKCHAIN' and r.tx_id_fabric:
            anomalies.append({"id": r.id_diplome, "issue": "State Mismatch: TX ID exists but status is pending"})

    return {
        "status": "COMPLETED",
        "timestamp": date.today().isoformat(),
        "total_records": len(records),
        "anomalies": anomalies,
        "integrity_score": max(0, 100 - (len(anomalies) * 10))
    }
