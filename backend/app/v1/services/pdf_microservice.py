import logging
import hashlib

logger = logging.getLogger(__name__)

class PDFClient:
    async def generate(self, titre: str, etudiant_id: str, institution_id: int, **kwargs) -> tuple[bytes, str]:
        logger.info(f"[MOCK] Generating PDF for {titre}...")
        pdf_bytes = b"%PDF-1.4 [GENERATED MOCK]"
        hash_sha256 = hashlib.sha256(pdf_bytes).hexdigest()
        return pdf_bytes, hash_sha256

pdf_client = PDFClient()
