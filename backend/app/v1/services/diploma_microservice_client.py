import hashlib
import logging
import uuid
from typing import Optional
from core.config import settings

logger = logging.getLogger(__name__)

class DiplomaMicroserviceClient:
    """
    Prepare integration for a Diploma Generation Microservice.
    Responsibilities:
    • send diploma generation request
    • receive diploma PDF
    • calculate SHA256 hash
    • store metadata in database
    """
    def __init__(self):
        self.url = settings.PDF_SERVICE_URL or "http://localhost:8001"
        self.api_key = getattr(settings, "MICROSERVICE_API_KEY", "DEMO_KEY")

    async def generate_diploma_via_microservice(self, diploma_id: int):
        """
        1 retrieve diploma data (Handled by caller/service)
        2 send request to microservice
        3 receive response
        4 update diplome_blockchain_ext (Handled by caller/service)
        """
        logger.info(f"Generating diploma {diploma_id} via microservice at {self.url}")
        
        # Simulating microservice response
        mock_pdf_content = f"PDF content for diploma {diploma_id}".encode()
        sha256_hash = hashlib.sha256(mock_pdf_content).hexdigest()
        
        return {
            "pdf_bytes": mock_pdf_content,
            "hash_sha256": sha256_hash,
            "success": True
        }

# Global instance
diploma_microservice_client = DiplomaMicroserviceClient()
