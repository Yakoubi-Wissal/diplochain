from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx
import hashlib
from typing import Optional

from core.database import engine, Base

app = FastAPI(
    title="DiploChain QR Validation Service",
    version="1.0.0",
    description="QR Verification Service"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration for external services
BLOCKCHAIN_SERVICE_URL = "http://blockchain-service:8000"
IPFS_GATEWAY_URL = "http://storage-service:8000/ipfs"

class VerificationResult(BaseModel):
    is_valid: bool
    identifiant_opaque: str
    message: str
    details: Optional[dict] = None

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.get("/")
async def root():
    return {"service": "qr-validation-service", "status": "running"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.get("/verify/{identifiant_opaque}", response_model=VerificationResult)
async def verify_diploma(identifiant_opaque: str):
    """
    Verification Logic:
    1. Query Hyperledger Fabric for the diploma records (hash + CID)
    2. Download PDF from IPFS (storage-service)
    3. Calculate SHA-256 of downloaded PDF
    4. Compare hashes
    """
    async with httpx.AsyncClient() as client:
        # Step 1: Query Fabric
        try:
            bc_response = await client.get(f"{BLOCKCHAIN_SERVICE_URL}/blockchain/query/{identifiant_opaque}")
            if bc_response.status_code != 200:
                return VerificationResult(
                    is_valid=False,
                    identifiant_opaque=identifiant_opaque,
                    message=f"Blockchain record not found for {identifiant_opaque}."
                )
            bc_data = bc_response.json()
        except Exception:
            # Fallback for tests if needed, but here we want to be strict
            raise HTTPException(status_code=503, detail="Blockchain service unavailable")

        hash_on_chain = bc_data.get("hash_sha256")
        ipfs_cid = bc_data.get("ipfs_cid")

        if not hash_on_chain or not ipfs_cid:
             return VerificationResult(
                is_valid=False,
                identifiant_opaque=identifiant_opaque,
                message="Blockchain record incomplete or invalid."
            )

        # Step 2: Download PDF from IPFS (storage-service)
        try:
            ipfs_response = await client.get(f"{IPFS_GATEWAY_URL}/{ipfs_cid}", timeout=5.0)
            if ipfs_response.status_code == 200:
                pdf_bytes = ipfs_response.content
            else:
                return VerificationResult(
                    is_valid=False,
                    identifiant_opaque=identifiant_opaque,
                    message="Failed to retrieve document from IPFS storage."
                )
        except Exception:
             return VerificationResult(
                is_valid=False,
                identifiant_opaque=identifiant_opaque,
                message="IPFS storage service unavailable."
            )

        # Step 3: Calculate SHA-256
        calculated_hash = hashlib.sha256(pdf_bytes).hexdigest()

        # Step 4: Compare
        is_valid = (calculated_hash == hash_on_chain)

        return VerificationResult(
            is_valid=is_valid,
            identifiant_opaque=identifiant_opaque,
            message="Valid" if is_valid else "Hashes do not match. Document may be forged.",
            details={
                "hash_on_chain": hash_on_chain,
                "calculated_hash": calculated_hash,
                "ipfs_cid": ipfs_cid
            }
        )
