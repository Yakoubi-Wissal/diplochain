from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class QrCodeRecordBase(BaseModel):
    diplome_id: int
    etudiant_id: str
    qr_code_path: str
    identifiant_opaque: str
    url_verification: str
    created_at: Optional[datetime]

class QrCodeRecordRead(QrCodeRecordBase):
    qr_code_records_id: int
    model_config = {"from_attributes": True}

class HistoriqueOperationBase(BaseModel):
    diplome_id: int
    type_operation: str
    ancien_hash: Optional[str]
    nouvel_hash: str
    tx_id_fabric: str
    acteur_id: int
    ip_address: Optional[str]
    ms_tenant_id: Optional[str]
    commentaire: Optional[str]
    user_agent: Optional[str]
    timestamp: Optional[datetime]

class HistoriqueOperationRead(HistoriqueOperationBase):
    historique_operations_id: int
    model_config = {"from_attributes": True}
