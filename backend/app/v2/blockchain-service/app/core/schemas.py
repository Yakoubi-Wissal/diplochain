from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime

class DiplomaBlockchainBase(BaseModel):
    titre: Optional[str] = None
    mention: Optional[str] = None
    date_emission: Optional[date] = None
    annee_promotion: Optional[str] = None
    hash_sha256: Optional[str] = None
    tx_id_fabric: Optional[str] = None
    ipfs_cid: Optional[str] = None
    statut: Optional[str] = None
    blockchain_retry_count: Optional[int] = 0
    blockchain_last_retry: Optional[datetime] = None
    generation_mode: Optional[str] = None
    template_id: Optional[int] = None
    institution_id: Optional[int] = None
    specialite_id: Optional[str] = None
    uploaded_by: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class DiplomaBlockchainCreate(DiplomaBlockchainBase):
    id_diplome: int

class DiplomaBlockchainRead(DiplomaBlockchainBase):
    id_diplome: int
    model_config = {"from_attributes": True}
