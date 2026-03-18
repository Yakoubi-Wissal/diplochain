from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text,select

from core.database import AsyncSessionLocal
from core.models import IPFSFile, PinningStatus
from core.schemas import IPFSFileCreate, IPFSFileRead

router = APIRouter(prefix="", tags=["Storage"])

async def get_db():
    async with AsyncSessionLocal() as s:
        yield s

@router.get("/health", tags=["Health"])
async def health():
    return {"status": "ok"}

@router.post("/files", response_model=IPFSFileRead)
async def create_file(rec: IPFSFileCreate, db: AsyncSession = Depends(get_db)):
    f = IPFSFile(cid=rec.cid, status=rec.status)
    db.add(f)
    await db.commit()
    await db.refresh(f)
    return f

@router.get("/files/{cid}", response_model=IPFSFileRead)
async def get_file(cid: str, db: AsyncSession = Depends(get_db)):
     
    result = await db.execute(select(IPFSFile).where(IPFSFile.cid == cid))
    f = result.scalar_one_or_none()
    if not f:
        raise HTTPException(status_code=404, detail="CID not found")
    return f
