from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from database import get_db
from models import User, Institution
from core.dependencies import require_role
from services.diploma_service import DiplomaService
from schemas import DiplomeRead
from utils.diplome_serializer import to_diplome_response  # returns DiplomeRead
from pydantic import BaseModel
from datetime import date

router = APIRouter(tags=["Verification"])

# public response schema with additional info
class VerificationRead(BaseModel):
    diploma_id: str
    student: str | None = None
    university: str | None = None
    degree: str | None = None
    field_of_study: str | None = None
    issue_date: date | None = None
    blockchain_hash: str | None = None
    status: str


# helper used by tests
def to_verification_response(diploma) -> dict:
    # build minimal verification dictionary from diploma + ext
    ext = diploma.blockchain_ext
    student = None
    if diploma.etudiant:
        student = f"{diploma.etudiant.prenom or ''} {diploma.etudiant.nom or ''}".strip() or None
    university = None
    if ext.institution_id:
        # attempt to fetch institution name later if needed
        pass
    status = "VERIFIED"
    if ext.statut == "REVOQUE":
        status = "REVOKED"
    elif not ext.hash_sha256:
        status = "INVALID"
    return {
        "diploma_id": f"DIP-{diploma.id_diplome:06d}",
        "student": student,
        "university": university,
        "degree": ext.titre,
        "field_of_study": ext.mention,
        "issue_date": ext.date_emission,
        "blockchain_hash": ext.hash_sha256,
        "status": status,
    }


@router.get("/verify/{identifier}", response_model=VerificationRead)
async def public_verify(
    identifier: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Public diploma verification (ID or QR token). No authentication required."""
    # verification workflow independent of Postgres
    # parse diploma id from identifier (either numeric or DIP- prefix)
    raw = identifier.upper().replace("DIP-", "")
    try:
        diplome_id = str(int(raw))
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid diploma identifier")

    # query blockchain to obtain stored hash + cid
    from services.fabric_service import fabric_service
    raw_bc = fabric_service.query_diploma(diplome_id)
    # support sync or async implementation (tests return plain dict)
    import asyncio
    if asyncio.iscoroutine(raw_bc):
        bc = await raw_bc
    else:
        bc = raw_bc
    if not bc or "hash_sha256" not in bc or "ipfs_cid" not in bc:
        raise HTTPException(status_code=404, detail="Diploma not found on blockchain")

    hash_onchain = bc.get("hash_sha256")
    cid_onchain  = bc.get("ipfs_cid")

    # fetch PDF from IPFS and recompute
    from services.ipfs_service import ipfs_service
    try:
        raw_pdf = ipfs_service.cat(cid_onchain)
        if asyncio.iscoroutine(raw_pdf):
            pdf_bytes = await raw_pdf
        else:
            pdf_bytes = raw_pdf
    except Exception:
        raise HTTPException(status_code=502, detail="Unable to retrieve file from IPFS")

    import hashlib
    real_hash = hashlib.sha256(pdf_bytes).hexdigest()
    status = "INVALID"
    if real_hash == hash_onchain:
        status = bc.get("status", "VERIFIED")
    # if chain marks revoked, override
    if bc.get("status") == "REVOKED":
        status = "REVOKED"

    # record audit log even for public
    # we don't know actor, but store ip
    from models import HistoriqueOperation, TypeOperation
    try:
        core_id = int(diplome_id)
        # save minimal audit row
        await db.execute(
            text(
                "INSERT INTO historique_operations (diplome_id, type_operation, nouvel_hash, ip_address) VALUES (:did, :op, :h, :ip)"
            ),
            {"did": core_id, "op": TypeOperation.VERIFICATION, "h": real_hash, "ip": request.client.host if request.client else None}
        )
        await db.commit()
    except Exception:
        pass

    # construct response
    resp = {
        "diploma_id": f"DIP-{int(diplome_id):06d}",
        "student": None,
        "university": bc.get("institution_name"),
        "degree": bc.get("titre"),
        "field_of_study": bc.get("mention"),
        "issue_date": bc.get("date_emission"),
        "blockchain_hash": hash_onchain,
        "status": status,
    }
    return resp
