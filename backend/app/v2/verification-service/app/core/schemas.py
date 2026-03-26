from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class QrCodeRecordBase(BaseModel):
    diplome_id: int
    etudiant_id: str
    qr_code_path: Optional[str] = None
    identifiant_opaque: Optional[str] = None
    url_verification: Optional[str] = None
    created_at: Optional[datetime] = None

class QrCodeRecordRead(QrCodeRecordBase):
    qr_code_records_id: int
    model_config = {"from_attributes": True}

class HistoriqueOperationBase(BaseModel):
    diplome_id: int
    type_operation: str
    ancien_hash: Optional[str] = None
    nouvel_hash: str
    tx_id_fabric: str
    acteur_id: int
    ip_address: Optional[str] = None
    ms_tenant_id: Optional[str] = None
    commentaire: Optional[str] = None
    user_agent: Optional[str] = None
    timestamp: Optional[datetime] = None

class HistoriqueOperationRead(HistoriqueOperationBase):
    historique_operations_id: int
    model_config = {"from_attributes": True}
