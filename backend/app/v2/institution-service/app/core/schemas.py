from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import date, datetime
from uuid import UUID

class InstitutionBase(BaseModel):
    nom_institution: Optional[str] = Field(None, max_length=255)
    adresse: Optional[str] = None
    code_postal: Optional[str] = None
    ville: Optional[str] = None
    date_creation: Optional[date] = None
    pays: Optional[str] = None
    telephone: Optional[str] = None
    email_institution: Optional[EmailStr] = None
    site_web: Optional[str] = None
    chiffre_affaires: Optional[float] = None
    nombre_employes: Optional[int] = None
    description: Optional[str] = None
    id_group_institution: Optional[int] = None

class InstitutionCreate(InstitutionBase):
    nom_institution: str
    email_institution: EmailStr
    date_creation: date

class InstitutionRead(InstitutionBase):
    institution_id: int
    date_mise_a_jour: Optional[datetime]
    model_config = {"from_attributes": True}

class InstitutionBlockchainBase(BaseModel):
    channel_id: Optional[str]
    peer_node_url: Optional[str]
    status: Optional[str]
    code: Optional[str]

class InstitutionBlockchainRead(InstitutionBlockchainBase):
    institution_id: int
    created_at: Optional[datetime]
    model_config = {"from_attributes": True}

# additional schemas for specialite_ext and template_departement can be added later
