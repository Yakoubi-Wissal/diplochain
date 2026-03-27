from fastapi import APIRouter, Depends, HTTPException
import httpx
import hashlib
import os

router = APIRouter(prefix="", tags=["QR Validation"])

BLOCKCHAIN_SERVICE_URL = os.getenv("BLOCKCHAIN_SERVICE_URL", "http://blockchain-service:8000")
STORAGE_SERVICE_URL = os.getenv("STORAGE_SERVICE_URL", "http://storage-service:8000")

@router.get("/v/health", tags=["Health"]) # Distinguish from main app health
async def router_health():
    return {"status": "ok"}

@router.get("/verify/{identifiant_opaque}")
async def verify_qr(identifiant_opaque: str):
    async with httpx.AsyncClient() as client:
        bc_resp = await client.get(f"{BLOCKCHAIN_SERVICE_URL}/blockchain/diplome/{identifiant_opaque}")
        if bc_resp.status_code != 200:
            raise HTTPException(status_code=404, detail="Blockchain record not found")

        bc_data = bc_resp.json()
        expected_hash = bc_data.get("hash_sha256")
        ipfs_cid = bc_data.get("ipfs_cid")

        ipfs_resp = await client.get(f"{STORAGE_SERVICE_URL}/ipfs/{ipfs_cid}")
        if ipfs_resp.status_code != 200:
            raise HTTPException(status_code=404, detail="Document not found on IPFS")

        actual_hash = hashlib.sha256(ipfs_resp.content).hexdigest()
        is_valid = (actual_hash == expected_hash)

        return {
            "identifiant_opaque": identifiant_opaque,
            "is_valid": is_valid,
            "blockchain_hash": expected_hash,
            "actual_hash": actual_hash,
            "status": bc_data.get("status")
        }
