"""
schemas.py — DiploChain Schema v6.0
Pydantic v2 schemas alignés sur le nouveau schéma.
"""

from __future__ import annotations

import uuid
from datetime import date, datetime
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, EmailStr


# ──────────────────────────────────────────────
# 1. Miroirs Python des ENUMs PostgreSQL v6.0
# ──────────────────────────────────────────────

class StatutDiplome(str, Enum):
    ORIGINAL = 'ORIGINAL'
    DUPLICATA = 'DUPLICATA'
    ANNULE = 'ANNULE'
    REVOQUE = 'REVOQUE'
    PENDING_BLOCKCHAIN = 'PENDING_BLOCKCHAIN'
    CONFIRME = 'CONFIRME'

class StatutInstitution(str, Enum):
    ACTIVE = 'ACTIVE'
    INACTIVE = 'INACTIVE'
    SUSPENDED = 'SUSPENDED'

class StatutValidation(str, Enum):
    EN_ATTENTE = 'EN_ATTENTE'
    VALIDE = 'VALIDE'
    REFUSE = 'REFUSE'

class TypeOperation(str, Enum):
    EMISSION = 'EMISSION'
    REVOCATION = 'REVOCATION'
    VERIFICATION = 'VERIFICATION'
    MISE_A_JOUR = 'MISE_A_JOUR'

class StatutUserDiploChain(str, Enum):
    EN_ATTENTE = 'EN_ATTENTE'
    ACTIF = 'ACTIF'
    SUSPENDU = 'SUSPENDU'
    DESACTIVE = 'DESACTIVE'

class GenerationMode(str, Enum):
    UPLOAD = "UPLOAD"
    MICROSERVICE = "MICROSERVICE"


# ──────────────────────────────────────────────
# 2. Auth
# ──────────────────────────────────────────────

class LoginRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ──────────────────────────────────────────────
# 3. Role
# ──────────────────────────────────────────────

class RoleRead(BaseModel):
    id_role: int
    code: str
    label_role: Optional[str] = None
    # Extension fields
    description: Optional[str] = None
    permissions: Optional[List[str]] = None
    is_active: bool = True
    
    model_config = {"from_attributes": True}


# ──────────────────────────────────────────────
# 4. Institution
# ──────────────────────────────────────────────

class InstitutionRead(BaseModel):
    institution_id: int
    nom_institution: str
    code: Optional[str] = None
    status: StatutInstitution = StatutInstitution.ACTIVE
    # Extension fields
    channel_id: Optional[str] = None
    peer_node_url: Optional[str] = None
    
    model_config = {"from_attributes": True}


# ──────────────────────────────────────────────
# 5. User
# ──────────────────────────────────────────────

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    # other fields may be added as needed

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    # allow partial updates of ext/core as needed

class UserRead(BaseModel):
    user_id: int
    email: EmailStr
    # Extension fields
    nom: Optional[str] = None
    prenom: Optional[str] = None
    statut_diplochain: StatutUserDiploChain
    niveau_acces: Optional[str] = "GLOBAL"
    blockchain_address: Optional[str] = None
    numero_etudiant: Optional[str] = None
    date_naissance: Optional[date] = None
    promotion: Optional[str] = None
    
    role_id: int
    institution_id: Optional[int] = None
    entreprise_id: Optional[int] = None
    
    model_config = {"from_attributes": True}


# ──────────────────────────────────────────────
# 6. Diplome
# ──────────────────────────────────────────────

class DiplomeRead(BaseModel):
    id_diplome: int
    etudiant_id: str
    date_emission: date
    # Extension fields
    titre: Optional[str] = None
    mention: Optional[str] = None
    hash_sha256: Optional[str] = None
    tx_id_fabric: Optional[str] = None
    ipfs_cid: Optional[str] = None
    statut: StatutDiplome
    generation_mode: GenerationMode
    
    institution_id: Optional[int] = None
    specialite_id: Optional[str] = None
    
    model_config = {"from_attributes": True}


class SpecialiteRead(BaseModel):
    code_specialite: str
    designation_specialite: str
    nom: Optional[str] = None
    code_ext: Optional[str] = None
    institution_id: Optional[int] = None
    is_active: bool = True

    model_config = {"from_attributes": True}


# ──────────────────────────────────────────────
# 7. Operational
# ──────────────────────────────────────────────

class HistoriqueOperationRead(BaseModel):
    historique_operations_id: int
    diplome_id: int
    type_operation: TypeOperation
    ancien_hash: Optional[str] = None
    nouvel_hash: str
    tx_id_fabric: str
    acteur_id: int
    ip_address: Optional[str] = None
    timestamp: datetime
    
    model_config = {"from_attributes": True}

class QrCodeRead(BaseModel):
    qr_code_records_id: int
    diplome_id: int
    etudiant_id: str
    identifiant_opaque: str
    url_verification: str
    qr_code_path: str
    created_at: datetime
    
    model_config = {"from_attributes": True}

class DiplomasPerStudent(BaseModel):
    etudiant_id: str
    nom: str
    prenom: str
    email: Optional[str] = None
    numero_etudiant: Optional[str] = None
    nb_diplomes_total: int
    nb_confirmes: int
    nb_pending: int
    nb_revoques: int
    derniere_emission: Optional[date] = None

    model_config = {"from_attributes": True}


class DiplomasPerInstitution(BaseModel):
    institution_id: int
    nom: str
    code: Optional[str] = None
    statut: Optional[str] = None
    nb_diplomes_total: int
    nb_via_microservice: int
    nb_via_upload: int
    nb_pending: int
    nb_revoques: int
    derniere_emission: Optional[date] = None

    model_config = {"from_attributes": True}


class DashboardMetricsRead(BaseModel):
    metric_date: date
    nb_diplomes_emis: int
    nb_diplomes_microservice: int
    nb_diplomes_upload: int
    nb_nouveaux_etudiants: int
    nb_institutions_actives: int
    nb_diplomes_confirmes: int
    nb_diplomes_pending: int
    nb_diplomes_revoques: int
    nb_verifications: int
    updated_at: datetime
    
    model_config = {"from_attributes": True}


# ──────────────────────────────────────────────
# 8. Dashboard View Schemas
# ──────────────────────────────────────────────

class DiplomasPerStudent(BaseModel):
    etudiant_id: str
    nom: Optional[str]
    prenom: Optional[str]
    email: Optional[EmailStr]
    numero_etudiant: Optional[str]
    nb_diplomes_total: int
    nb_confirmes: int
    nb_pending: int
    nb_revoques: int
    derniere_emission: Optional[date]

    model_config = {"from_attributes": True}

class DiplomasPerInstitution(BaseModel):
    institution_id: int
    nom: Optional[str]
    code: Optional[str]
    statut: Optional[StatutInstitution]
    nb_diplomes_total: int
    nb_via_microservice: int
    nb_via_upload: int
    nb_pending: int
    nb_revoques: int
    derniere_emission: Optional[date]

    model_config = {"from_attributes": True}
