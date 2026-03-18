from pydantic import BaseModel, ConfigDict
from datetime import date, datetime
from typing import Optional

class DiplomaBase(BaseModel):
    # etudiant_diplome fields
    etudiant_id: str
    session_diplome: str = "Principale"
    id_annexe: int = 1
    num_diplome: int = 1
    date_diplome: date = date.today()
    date_liv_diplome: date = date.today()
    
    # diplome_blockchain_ext fields
    titre: str
    mention: Optional[str] = None
    date_emission: date = date.today()
    annee_promotion: Optional[str] = None
    hash_sha256: str
    ipfs_cid: str
    statut: Optional[str] = "ORIGINAL"
    generation_mode: Optional[str] = "UPLOAD"
    template_id: Optional[int] = None
    institution_id: int
    specialite_id: Optional[str] = None
    uploaded_by: int

class DiplomaCreate(DiplomaBase):
    pass

class DiplomaUpdate(BaseModel):
    titre: Optional[str] = None
    mention: Optional[str] = None
    statut: Optional[str] = None
    ipfs_cid: Optional[str] = None

class DiplomaRead(DiplomaBase):
    id_diplome: int
    tx_id_fabric: Optional[str] = None
    blockchain_retry_count: Optional[int] = 0
    blockchain_last_retry: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
