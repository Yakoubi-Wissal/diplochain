import logging
import uuid
from core.config import settings

logger = logging.getLogger(__name__)

class BlockchainClient:
    """
    Prepare integration with a Blockchain service.
    Responsibilities:
    • register diploma hash on blockchain
    • receive transaction id
    • update database
    """
    def __init__(self):
        self.api_url = getattr(settings, "BLOCKCHAIN_API_URL", "http://fabric-service:9000")

    async def register_diploma_hash(self, hash_sha256: str) -> str:
        """
        Expected response: tx_id_fabric
        For now: simulate the blockchain response.
        """
        logger.info(f"Registering hash {hash_sha256} on blockchain at {self.api_url}")
        
        # Simulate Hyperledger Fabric TX ID
        tx_id_fabric = f"tx_{uuid.uuid4().hex}"
        return tx_id_fabric

    async def revoke_diploma(self, tx_id: str) -> str:
        logger.info(f"Revoking diploma on blockchain (TX: {tx_id})")
        return f"revoke_{uuid.uuid4().hex}"

# Global instance
blockchain_client = BlockchainClient()
