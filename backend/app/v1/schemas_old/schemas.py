"""
schemas.py — DiploChain
Schémas Pydantic de validation / sérialisation pour l'API.
Alignés sur le schéma fusionné.
"""

from __future__ import annotations

import uuid
from datetime import date, datetime
from typing import List, Optional
from enum import Enum

from pydantic import BaseModel, EmailStr, Field, field_validator


# ─────────────────────────────────────────────────────────────────────────────
#  ENUMS Python (miroir des enums PostgreSQL)
# ─────────────────────────────────────────────────────────────────────────────

class StatutInstitution(str, Enum):
    ACTIVE    = "ACTIVE"
    SUSPENDUE = "SUSPENDUE"
    ARCHIVEE  = "ARCHIVEE"


class StatutUser(str, Enum):
    ACTIF      = "ACTIF"
    EN_ATTENTE = "EN_ATTENTE"
    SUSPENDU   = "SUSPENDU"


class StatutDiplome(str, Enum):
    PENDING_BLOCKCHAIN = "PENDING_BLOCKCHAIN"
    ORIGINAL           = "ORIGINAL"
    MODIFIE            = "MODIFIE"
    DUPLIQUE           = "DUPLIQUE"
    REVOQUE            = "REVOQUE"


class TypeOperation(str, Enum):
    CREATION     = "CREATION"
    MODIFICATION = "MODIFICATION"
    REVOCATION   = "REVOCATION"
    DUPLICATION  = "DUPLICATION"
    VERIFICATION = "VERIFICATION"


class StatutValidation(str, Enum):
    EN_ATTENTE = "EN_ATTENTE"
    APPROUVEE  = "APPROUVEE"
    REFUSEE    = "REFUSEE"


class GenerationMode(str, Enum):
    UPLOAD       = "UPLOAD"
    MICROSERVICE = "MICROSERVICE"


# ─────────────────────────────────────────────────────────────────────────────
#  AUTH
# ─────────────────────────────────────────────────────────────────────────────

class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ─────────────────────────────────────────────────────────────────────────────
#  ROLE
# ─────────────────────────────────────────────────────────────────────────────

class RoleBase(BaseModel):
    label_role:  Optional[str]       = None
    code:        str
    description: Optional[str]       = None
    permissions: Optional[List[str]] = None
    is_active:   bool                = True


class RoleCreate(RoleBase):
    pass


class RoleRead(RoleBase):
    id_role:    int
    created_at: datetime

    model_config = {"from_attributes": True}


# ─────────────────────────────────────────────────────────────────────────────
#  INSTITUTION
# ─────────────────────────────────────────────────────────────────────────────

class InstitutionBase(BaseModel):
    nom_institution:   Optional[str] = None
    adresse:           Optional[str] = None
    code_postal:       Optional[str] = None
    ville:             Optional[str] = None
    pays:              Optional[str] = None
    telephone:         Optional[str] = None
    email_institution: Optional[str] = None
    site_web:          Optional[str] = None
    description:       Optional[str] = None
    # [V6]
    channel_id:    Optional[str]            = None
    peer_node_url: Optional[str]            = None
    statut:        StatutInstitution        = StatutInstitution.ACTIVE
    code:          Optional[str]            = None


class InstitutionCreate(InstitutionBase):
    institution_id: int


class InstitutionUpdate(BaseModel):
    nom_institution:   Optional[str]            = None
    statut:            Optional[StatutInstitution] = None
    channel_id:        Optional[str]            = None
    peer_node_url:     Optional[str]            = None
    code:              Optional[str]            = None


class InstitutionRead(InstitutionBase):
    institution_id: int
    uuid_id:        Optional[uuid.UUID] = None

    model_config = {"from_attributes": True}


# ─────────────────────────────────────────────────────────────────────────────
#  SPECIALITE
# ─────────────────────────────────────────────────────────────────────────────

class SpecialiteBase(BaseModel):
    code_specialite:        str
    designation_specialite: Optional[str] = None
    institution_id:         Optional[int] = None
    is_active:              bool          = True


class SpecialiteCreate(SpecialiteBase):
    pass


class SpecialiteRead(SpecialiteBase):
    uuid_id:    Optional[uuid.UUID] = None
    created_at: Optional[datetime]  = None

    model_config = {"from_attributes": True}


# ─────────────────────────────────────────────────────────────────────────────
#  USER
# ─────────────────────────────────────────────────────────────────────────────

class UserBase(BaseModel):
    username:        Optional[str]      = None
    email:           Optional[str]      = None
    nom:             Optional[str]      = None
    prenom:          Optional[str]      = None
    role_id:         Optional[int]      = None
    institution_id:  Optional[int]      = None
    entreprise_id:   Optional[int]      = None
    numero_etudiant: Optional[str]      = None
    promotion:       Optional[str]      = None
    statut_diplochain: StatutUser       = StatutUser.EN_ATTENTE


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)


class UserUpdate(BaseModel):
    nom:              Optional[str]       = None
    prenom:           Optional[str]       = None
    email:            Optional[str]       = None
    role_id:          Optional[int]       = None
    institution_id:   Optional[int]       = None
    statut_diplochain: Optional[StatutUser] = None
    promotion:        Optional[str]       = None
    numero_etudiant:  Optional[str]       = None


class UserRead(UserBase):
    id_user:    int
    created_at: datetime
    uuid_id:    Optional[uuid.UUID] = None
    role:       Optional[RoleRead]  = None

    model_config = {"from_attributes": True}


# ─────────────────────────────────────────────────────────────────────────────
#  DIPLOME
# ─────────────────────────────────────────────────────────────────────────────

class DiplomeBase(BaseModel):
    titre:          str
    mention:        Optional[str]          = None
    institution_id: int
    specialite_id:  Optional[str]          = None
    etudiant_id:    int
    date_emission:  date                   = Field(default_factory=date.today)
    annee_promotion: Optional[str]         = None
    generation_mode: GenerationMode        = GenerationMode.UPLOAD


class DiplomeCreate(DiplomeBase):
    hash_sha256: str = Field(..., min_length=64, max_length=64)
    ipfs_cid:    str


class DiplomeRead(DiplomeBase):
    id:                     uuid.UUID
    statut:                 StatutDiplome
    hash_sha256:            str
    ipfs_cid:               str
    tx_id_fabric:           Optional[str]      = None
    blockchain_retry_count: int
    created_at:             datetime
    updated_at:             datetime

    model_config = {"from_attributes": True}


class DiplomeUpdateStatut(BaseModel):
    statut:      StatutDiplome
    tx_id_fabric: Optional[str] = None


# ─────────────────────────────────────────────────────────────────────────────
#  HISTORIQUE OPERATION
# ─────────────────────────────────────────────────────────────────────────────

class HistoriqueOperationCreate(BaseModel):
    diplome_id:     uuid.UUID
    type_operation: TypeOperation
    ancien_hash:    Optional[str] = None
    nouvel_hash:    Optional[str] = None
    tx_id_fabric:   Optional[str] = None
    commentaire:    Optional[str] = None


class HistoriqueOperationRead(HistoriqueOperationCreate):
    id:        uuid.UUID
    acteur_id: int
    timestamp: datetime
    ip_address: Optional[str] = None

    model_config = {"from_attributes": True}


# ─────────────────────────────────────────────────────────────────────────────
#  QR CODE
# ─────────────────────────────────────────────────────────────────────────────

class QrCodeRead(BaseModel):
    id:                 uuid.UUID
    diplome_id:         uuid.UUID
    identifiant_opaque: str
    url_verification:   str
    qr_code_data:       Optional[str] = None
    is_active:          bool
    created_at:         datetime

    model_config = {"from_attributes": True}


# ─────────────────────────────────────────────────────────────────────────────
#  ENTREPRISE
# ─────────────────────────────────────────────────────────────────────────────

class EntrepriseBase(BaseModel):
    nom_entreprise:        str
    raison_sociale:        Optional[str]       = None
    matricule_fiscale:     Optional[str]       = None
    secteur_activite:      Optional[str]       = None
    email_entreprise:      Optional[str]       = None
    microsoft_tenant_id:   Optional[str]       = None
    microsoft_email_domain: Optional[str]      = None


class EntrepriseCreate(EntrepriseBase):
    pass


class EntrepriseRead(EntrepriseBase):
    id_entreprise: int
    statut:        StatutValidation
    uuid_id:       Optional[uuid.UUID] = None

    model_config = {"from_attributes": True}


class EntrepriseValidationAction(BaseModel):
    action:      StatutValidation   # APPROUVEE ou REFUSEE
    motif_refus: Optional[str]      = None


# ─────────────────────────────────────────────────────────────────────────────
#  DASHBOARD
# ─────────────────────────────────────────────────────────────────────────────

class DashboardMetricsRead(BaseModel):
    metric_date:              date
    nb_diplomes_emis:         int
    nb_diplomes_microservice: int
    nb_diplomes_upload:       int
    nb_nouveaux_etudiants:    int
    nb_institutions_actives:  int
    nb_diplomes_confirmes:    int
    nb_diplomes_pending:      int
    nb_diplomes_revoques:     int
    nb_verifications:         int
    updated_at:               datetime

    model_config = {"from_attributes": True}