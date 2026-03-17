from pydantic import BaseModel, Field
from datetime import date
from typing import Optional
from uuid import UUID

class DiplomaBase(BaseModel):
    titre: str
    mention: Optional[str]
    date_emission: date
    hash_sha256: str
    ipfs_cid: str
    statut: Optional[str] = Field(default="ORIGINAL")
    etudiant_id: UUID
    institution_id: UUID
    specialite_id: Optional[UUID]
    template_id: Optional[UUID]
    uploaded_by: UUID

class DiplomaCreate(DiplomaBase):
    pass

class DiplomaUpdate(BaseModel):
    titre: Optional[str]
    mention: Optional[str]
    statut: Optional[str]
    ipfs_cid: Optional[str]

class DiplomaRead(DiplomaBase):
    id: UUID
    created_at: Optional[date]
    updated_at: Optional[date]

    model_config = {"from_attributes": True}
