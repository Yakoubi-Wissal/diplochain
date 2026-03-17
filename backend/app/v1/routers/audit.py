from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from core.dependencies import require_role
from database import get_db
from models import HistoriqueOperation
from schemas import HistoriqueOperationRead, TypeOperation

router = APIRouter(prefix="/api/audit", tags=["Audit"])

# we will accept a simplified create model for posting audits
from pydantic import BaseModel
from datetime import datetime

class AuditCreate(BaseModel):
    diploma_id: str | int
    status: str
    enterprise_id: Optional[int]
    timestamp: datetime

@router.post("/verification")
async def add_verification(record: AuditCreate, db: AsyncSession = Depends(get_db)):
    # normalize diploma id (allow DIP- prefix)
    raw = str(record.diploma_id)
    if isinstance(raw, str) and raw.upper().startswith("DIP-"):
        raw = raw.split("-", 1)[1]
    try:
        diplome_id = int(raw)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid diploma identifier")

    # when posting from enterprise we accept enterprise_id and log it in ms_tenant_id
    ent = str(record.enterprise_id) if record.enterprise_id is not None else None

    # using raw SQL to avoid FK constraint on acteur_id
    from sqlalchemy import text
    try:
        await db.execute(
            text(
                "INSERT INTO historique_operations (diplome_id, type_operation, nouvel_hash, ms_tenant_id) "
                "VALUES (:did, :op, :h, :ent)"
            ),
            {"did": diplome_id, "op": TypeOperation.VERIFICATION, "h": record.status, "ent": ent},
        )
        await db.commit()
    except Exception:
        # swallow errors (mimic public_verify behaviour)
        pass
    return {"status": "ok"}

@router.get("/verification", response_model=List[HistoriqueOperationRead])
async def list_verifications(
    enterprise_id: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_role("SUPER_ADMIN", "ENTERPRISE"))
):
    # base query for VERIFICATION operations
    query = select(HistoriqueOperation).where(HistoriqueOperation.type_operation == TypeOperation.VERIFICATION)
    if enterprise_id:
        # filter by ms_tenant_id column
        query = query.where(HistoriqueOperation.ms_tenant_id == enterprise_id)
    result = await db.execute(query.order_by(HistoriqueOperation.timestamp.desc()))
    rows = result.scalars().all()
    return rows
