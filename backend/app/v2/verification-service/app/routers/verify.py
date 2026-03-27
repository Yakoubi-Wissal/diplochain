from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from core.database import AsyncSessionLocal
from core.models import QrCodeRecord, HistoriqueOperation
from core.schemas import QrCodeRecordRead, QrCodeRecordBase, HistoriqueOperationRead

router = APIRouter(prefix="", tags=["Verify"])

async def get_db():
    async with AsyncSessionLocal() as s:
        yield s

@router.get("/v/health", tags=["Health"])
async def router_health():
    return {"status": "ok"}

@router.post("/qr", response_model=QrCodeRecordRead)
async def create_qr(record: QrCodeRecordBase, db: AsyncSession = Depends(get_db)):
    data = record.model_dump()
    if data.get("created_at") is None:
        data["created_at"] = datetime.utcnow()
    qr = QrCodeRecord(**data)
    db.add(qr)
    await db.commit()
    await db.refresh(qr)
    return qr

@router.get("/qr/{qr_id}", response_model=QrCodeRecordRead)
async def read_qr(qr_id: int, db: AsyncSession = Depends(get_db)):
    qr = await db.get(QrCodeRecord, qr_id)
    if not qr:
        raise HTTPException(status_code=404, detail="QR record not found")
    return qr

@router.get("/diploma/{diploma_id}")
async def verify_diploma_from_services(diploma_id: int):
    import httpx
    async with httpx.AsyncClient(timeout=5) as client:
        bc_resp = await client.get(f"http://blockchain-service:8000/blockchain/diplome/{diploma_id}")
    return {"blockchain": bc_resp.json()}

@router.post("/history", response_model=HistoriqueOperationRead)
async def record_history(entry: HistoriqueOperationRead, db: AsyncSession = Depends(get_db)):
    h = HistoriqueOperation(**entry.model_dump())
    db.add(h)
    await db.commit()
    await db.refresh(h)
    return h
