from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import date

class StudentBase(BaseModel):
    email_etudiant: Optional[EmailStr] = None
    nom: Optional[str] = None
    prenom: Optional[str] = None
    date_naissance: Optional[date] = None
    num_cin: Optional[str] = None
    num_passeport: Optional[str] = None
    entreprise_id: Optional[int] = None
    telephone: Optional[str] = None
    code_nationalite: Optional[str] = None
    code_specialite: Optional[str] = None
    date_delivrance: Optional[date] = None
    lieu_nais_et: Optional[str] = None
    sexe: Optional[str] = None
    lieu_delivrance: Optional[str] = None
    id_user: Optional[int] = None
    adresse_postale: Optional[str] = None
    code_postal: Optional[str] = None
    ville: Optional[str] = None
    gouvernorat: Optional[str] = None
    linkedin_id: Optional[str] = None
    linkedin_url: Optional[str] = None
    linkedin_data_id: Optional[int] = None
    email_esprit_etudiant: Optional[EmailStr] = None

class StudentCreate(StudentBase):
    etudiant_id: str

class StudentRead(StudentBase):
    etudiant_id: str
    model_config = {"from_attributes": True}
