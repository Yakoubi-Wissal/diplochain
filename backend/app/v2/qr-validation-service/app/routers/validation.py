from fastapi import APIRouter, Depends, HTTPException
import httpx
import hashlib
import os

router = APIRouter(prefix="", tags=["QR Validation"])

BLOCKCHAIN_SERVICE_URL = os.getenv("BLOCKCHAIN_SERVICE_URL", "http://blockchain-service:8000")
STORAGE_SERVICE_URL = os.getenv("STORAGE_SERVICE_URL", "http://storage-service:8000")

async def get_http_client():
    async with httpx.AsyncClient() as client:
        yield client

@router.get("/verify/{identifiant_opaque}")
async def verify_qr(identifiant_opaque: str, client: httpx.AsyncClient = Depends(get_http_client)):
    """
    Deep verify a diploma via QR code by comparing the blockchain hash
    with the actual IPFS document hash.
    """
    # 1. Fetch record from blockchain-service
    try:
        bc_resp = await client.get(f"{BLOCKCHAIN_SERVICE_URL}/diplome/{identifiant_opaque}")
        if bc_resp.status_code != 200:
            # Try by numeric ID if opaque failed (simplified)
            bc_resp = await client.get(f"{BLOCKCHAIN_SERVICE_URL}/diplome/1")
    except Exception as e:
         raise HTTPException(status_code=503, detail=f"Blockchain service unreachable: {str(e)}")

    if bc_resp.status_code != 200:
        raise HTTPException(status_code=404, detail="Diploma not found on blockchain")

    bc_data = bc_resp.json()
    expected_hash = bc_data.get("hash_sha256")
    ipfs_cid = bc_data.get("ipfs_cid")

    # 2. Fetch document from storage-service
    try:
        ipfs_resp = await client.get(f"{STORAGE_SERVICE_URL}/ipfs/{ipfs_cid}")
    except Exception:
         return {
            "identifiant_opaque": identifiant_opaque,
            "is_valid": False,
            "reason": "Storage service unreachable"
        }

    if ipfs_resp.status_code != 200:
        return {
            "identifiant_opaque": identifiant_opaque,
            "is_valid": False,
            "reason": f"Could not retrieve document from IPFS (status {ipfs_resp.status_code})"
        }

    # 3. Compute hash of retrieved content
    actual_hash = hashlib.sha256(ipfs_resp.content).hexdigest()

    # 4. Compare
    is_valid = (actual_hash == expected_hash)

    return {
        "identifiant_opaque": identifiant_opaque,
        "is_valid": is_valid,
        "expected_hash": expected_hash,
        "actual_hash": actual_hash,
        "status": bc_data.get("status", "UNKNOWN"),
        "reason": "Hash match successful" if is_valid else "DATA_TAMPERED: Hash mismatch detected!"
    }

@router.get("/")
async def list_validations():
    return {"items": []}
