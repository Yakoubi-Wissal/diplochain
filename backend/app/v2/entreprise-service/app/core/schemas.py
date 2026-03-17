from pydantic import BaseModel, EmailStr
from typing import Optional

class EntrepriseBase(BaseModel):
    nom_entreprise: Optional[str] = None
    secteur_activite: Optional[str] = None
    matricule_fiscale: Optional[str] = None
    email_contact: Optional[EmailStr] = None
    telephone: Optional[str] = None
    adresse: Optional[str] = None
    site_web: Optional[str] = None
    id_user: Optional[int] = None

class EntrepriseCreate(EntrepriseBase):
    nom_entreprise: str
    matricule_fiscale: str

class EntrepriseRead(EntrepriseBase):
    id: int
    nom_entreprise: str
    matricule_fiscale: str
    model_config = {"from_attributes": True}
