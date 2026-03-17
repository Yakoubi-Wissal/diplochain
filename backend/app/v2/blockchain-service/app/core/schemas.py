from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime

class DiplomaBlockchainBase(BaseModel):
    titre: Optional[str]
    mention: Optional[str]
    date_emission: Optional[date]
    annee_promotion: Optional[str]
    hash_sha256: Optional[str]
    tx_id_fabric: Optional[str]
    ipfs_cid: Optional[str]
    statut: Optional[str]
    blockchain_retry_count: Optional[int]
    blockchain_last_retry: Optional[datetime]
    generation_mode: Optional[str]
    template_id: Optional[int]
    institution_id: Optional[int]
    specialite_id: Optional[str]
    uploaded_by: Optional[int]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

class DiplomaBlockchainCreate(DiplomaBlockchainBase):
    id_diplome: int

class DiplomaBlockchainRead(DiplomaBlockchainBase):
    id_diplome: int
    model_config = {"from_attributes": True}
