import logging
import hashlib

logger = logging.getLogger(__name__)

class IpfsService:
    async def add_bytes(self, data: bytes) -> str:
        logger.info("[MOCK] Adding bytes to IPFS...")
        # Mock CID: Qm + hash of data
        return "Qm" + hashlib.md5(data).hexdigest()

    async def cat(self, cid: str) -> bytes:
        logger.info(f"[MOCK] Fetching {cid} from IPFS...")
        return b"%PDF-1.4 [MOCK DATA]"

ipfs_service = IpfsService()
