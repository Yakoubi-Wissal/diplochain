import logging
import uuid

logger = logging.getLogger(__name__)

class FabricService:
    async def register_diploma(self, diplome_id: str, hash_sha256: str, ipfs_cid: str, institution_id: str, etudiant_id: str, date_emission: str) -> str:
        logger.info(f"[MOCK] Registering diploma {diplome_id} on Fabric...")
        return f"tx_{uuid.uuid4().hex[:12]}"

    async def revoke_diploma(self, diplome_id: str, reason: str) -> str:
        logger.info(f"[MOCK] Revoking diploma {diplome_id} on Fabric...")
        return f"tx_revoke_{uuid.uuid4().hex[:12]}"

    async def query_diploma(self, diplome_id: str) -> dict:
        logger.info(f"[MOCK] Querying diploma {diplome_id} on Fabric...")
        # Return something to make verification logic pass (needs to match DB for testing)
        return {
            "diplome_id": diplome_id,
            "hash_sha256": "MOCK_HASH",
            "ipfs_cid": "MOCK_CID",
            "status": "ORIGINAL"
        }

fabric_service = FabricService()
